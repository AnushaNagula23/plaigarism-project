from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .utils import get_mongo_collection  # Import the helper function

class GetContestBySlugAPIView(APIView):
    """
    API to retrieve contest details using slug, fetching only selected fields.
    """

    def get(self, request, slug):
        # Get the contests collection using the helper function
        contests_collection = get_mongo_collection('contests')

        try:
            # Fetch contest based on slug and only return selected fields
            contest = contests_collection.find_one(
                {'slug': slug},  # Search for contest by slug
                {'_id': 0, 'slug': 1, 'title': 1, 'description': 1}  # Projection
            )

            if contest:
                return Response(contest, status=status.HTTP_200_OK)
            else:
                return Response({"error": "Contest not found."}, status=status.HTTP_404_NOT_FOUND)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
