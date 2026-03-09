# from rest_framework.views import APIView
# from rest_framework.response import Response
# from rest_framework import status
# from rest_framework import serializers
# from apps.common.auth.authentication import UnifiedJWTAuthentication
# from apps.common.permissions import HasDynamicPermission

# class FCMTokenUpdateSerializer(serializers.Serializer):
#     fcm_token = serializers.CharField(max_length=255, required=True)

# class FCMTokenUpdateView(APIView):
#     authentication_classes = [UnifiedJWTAuthentication]
#     permission_classes = [HasDynamicPermission(crud_perm="MAIN_PAGE", read_perm="MAIN_PAGE")]

#     def post(self, request):
#         serializer = FCMTokenUpdateSerializer(data=request.data)
#         if serializer.is_valid():
#             fcm_token = serializer.validated_data['fcm_token']
#             user = request.user
            
#             # Driver yoki FactoryUser ga qarab token yangilash
#             if user.__class__.__name__ == 'Driver':
#                 user.fcm_token = fcm_token
#                 user.save()
#             elif hasattr(user, 'role'):  # FactoryUser
#                 user.fcm_token = fcm_token
#                 user.save()
            
#             return Response({"message": "FCM token successfully updated"}, status=status.HTTP_200_OK)
        
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)