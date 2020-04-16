from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404
from django.contrib.auth import authenticate

from .models import Poll, Choice
from .serializers import (
    PollSerializer,
    ChoiceSerializer,
    VoteSerializer,
    UserSerializer
)


class PollList(generics.ListCreateAPIView):
    queryset = Poll.objects.all()
    serializer_class = PollSerializer


class PollDetail(generics.RetrieveDestroyAPIView):
    queryset = Poll.objects.all()
    serializer_class = PollSerializer

    def delete(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.created_by != request.user:
            raise PermissionDenied("You can not delete this poll")
        return self.destroy(request, *args, **kwargs)


class ChoiceList(generics.ListCreateAPIView):
    serializer_class = ChoiceSerializer

    def get_queryset(self):
        queryset = Choice.objects.filter(poll_id=self.kwargs['pk'])
        return queryset
    

    def post(self, request, *args, **kwargs):
        poll = Poll.objects.get(pk=self.kwargs['pk'])
        if request.user != poll.created_by:
            raise PermissionDenied("You can not create choice for this poll.")
        return self.create(request, *args, **kwargs)


class CreateVote(generics.CreateAPIView):
    serializer_class = VoteSerializer

    def create(self, request, *args, **kwargs):
        voted_by = request.data.get('voted_by')
        data = {'choice': kwargs['choice_pk'], 'poll': kwargs['pk'], 'voted_by':voted_by}
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)


class UserCreate(generics.CreateAPIView):
    authentication_classes = ()
    permission_classes = ()
    serializer_class = UserSerializer


class LoginView(APIView):
    permission_classes = ()
    
    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')
        user = authenticate(username=username, password=password)
        if user:
            return Response({"token": user.auth_token.key})
        else:
            return Response({"error", "Wrong Credentials"}, status=status.HTTP_400_BAD_REQUEST)
