from rest_framework.views import APIView
from rest_framework.response import Response
from data.session.models import TgLocationSessions
from rest_framework import status
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
import os

class TgLocationSessionView(APIView):
    def post(self, request):
        session = TgLocationSessions.objects.create()
        url = os.getenv("BOT_URL") + "?start=session{}".format(session.id)
        return Response(data={"session_id": str(session.id), "url": url}, status=status.HTTP_201_CREATED)

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter(
                name="session_id",
                in_=openapi.IN_QUERY,
                description="Session ID",
                type=openapi.TYPE_STRING,
                required=True
            )
        ],
        responses={200: "OK"}
    )
    def get(self, request): 
        session_id = request.query_params.get("session_id")
        if not session_id:
            return Response(data={"error": "session_id is required"}, status=status.HTTP_400_BAD_REQUEST)
        try:
            session = TgLocationSessions.objects.get(id=session_id)
        except TgLocationSessions.DoesNotExist:
            return Response(data={"error": "session not found"}, status=status.HTTP_404_NOT_FOUND)
        return Response(data={"session": {"id": str(session.id), "lat": session.lat, "lon": session.lon}}, status=status.HTTP_200_OK)