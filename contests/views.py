from collections import defaultdict
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .utils import get_mongo_collection  # Import the helper function

import boto3
from django.http import JsonResponse
import os



def retrieveDataFromDB(slug):
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
            return ({"error": "Contest not found."})

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
        return  {
            'contest id': str(contest_id),
            'submissions': grouped_submissions
        }
    except Exception as e:
        print(str(e))
        return {'error': str(e)}

class GetContestBySlugAPIView(APIView):
    """
    API to retrieve contest details and associated submissions for each problem.
    """

    def get(self, request, slug):
        
        try:
            data = retrieveDataFromDB(slug)
            if('error' in data):
               return Response(data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
               
            return Response({'Success':True, 'data': data}, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

def fetch_s3_files(request):
    
        
    # print(os.environ.get('AWS_ACCESS_KEY_ID'))
    # Initialize the S3 client
    s3 = boto3.client(
        's3',
        aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
        aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
        region_name=os.getenv('AWS_REGION')
    )
    
    bucket_name = 'connectiontestaws'
    try:
        # List objects in the S3 bucket
        response = s3.list_objects_v2(Bucket=bucket_name)
        
        # Check if the bucket contains any files
        if 'Contents' not in response:
            return JsonResponse({'message': 'No files found in the bucket'}, status=404)
        
        files = []
        for obj in response['Contents']:
            file_key = obj['Key']
            
            # Fetch file content
            file_object = s3.get_object(Bucket=bucket_name, Key=file_key)
            file_content = file_object['Body'].read().decode('utf-8')
            
            files.append({
                'file_name': file_key,
                'content': file_content,
            })
        
        return JsonResponse({'files': files})
    
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)