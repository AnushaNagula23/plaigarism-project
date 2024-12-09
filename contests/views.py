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
                    'participations': 1,
                    'window': 1
                }
            )

            if not contest:
                return Response({"error": "Contest not found."}, status=status.HTTP_404_NOT_FOUND)

            # Extract required data
            contest_id = contest['_id']
            participations = contest.get('participations', [])
            user_ids = [p['userId'] for p in participations]

            # Extract window start and end times
            window = contest.get('window', {})
            window_start = window.get('start')
            window_end = window.get('end')
            # Fetch submissions for each problem in the contest
            submissions = list(submissions_collection.find(
                {
                    'contestId': contest_id,
                    'userId': {'$in': user_ids},
                    'verdict': 'Accepted',
                    'solutions': {
                        '$elemMatch': {
                            'submittedAt': {'$gte': window_start, '$lte': window_end},
                            'verdict': 'Accepted'
                        }
                    }
                },
                {
                    '_id': 0,  # Exclude MongoDB ID
                    'userId': 1,
                    'problemId': 1,
                    'solutions': 1
                }
            ))
            
            grouped_submissions = defaultdict(list)
            for sub in submissions:
                problem_id = str(sub['problemId'])  # Convert ObjectId to string

                # Filter solutions based on submittedAt within the contest window
                filtered_solutions = [
                    {
                        'code': solution['code'],
                        'language': solution['language']
                    }
                    for solution in sub.get('solutions', [])
                    if window_start <= solution['submittedAt'] <= window_end and solution['verdict'] == 'Accepted'
                ]

                grouped_submissions[problem_id].append({
                    'userId': str(sub['userId']),  # Convert ObjectId to string
                    #'solutions': filtered_solutions  # Include only filtered solutions
                    'code': filtered_solutions[0].get('code'),
                    'language': filtered_solutions[0].get('language')
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
