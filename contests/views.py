from collections import defaultdict
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .utils import get_mongo_collection  # Import the helper function

class GetContestBySlugAPIView(APIView):
    """
    API to retrieve contest details and associated submissions for each problem.
    """

    def get(self, request, slug):
        contests_collection = get_mongo_collection('contests')
        submissions_collection = get_mongo_collection('submissions')

        try:
            # Fetch the required fields from the contest
            contest = contests_collection.find_one(
                {'slug': slug},
                {
                    '_id': 1,  # Contest ID
                    'batchIds': 1,
                    'participations': 1
                }
            )

            if not contest:
                return Response({"error": "Contest not found."}, status=status.HTTP_404_NOT_FOUND)

            # Extract required data
            contest_id = contest['_id']
            participations = contest.get('participations', [])
            user_ids = [participation['userId'] for participation in participations]

            # Fetch submissions for each problem in the contest
            submissions = list(submissions_collection.find(
                {
                    'contestId': contest_id,
                    'userId': {'$in': user_ids},
                    'verdict': 'Accepted'
                },
                {
                    '_id': 0,  # Exclude MongoDB ID
                    'userId': 1,
                    'problemId': 1,
                    'solutions': 1
                }
            ))
            
            grouped_submissions = defaultdict(list)
            for submission in submissions:
                problem_id = str(submission['problemId'])
                grouped_submissions[problem_id].append({
                    **submission,
                    'userId': str(submission['userId']),
                    'problemId': problem_id
                })

            # Convert defaultdict to a normal dict
            grouped_submissions = dict(grouped_submissions)

            return Response({
                'contestId': str(contest_id),
                'batchIds': contest.get('batchIds', []),
                'submissions': grouped_submissions
            }, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
