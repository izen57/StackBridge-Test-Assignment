from django.contrib.auth import authenticate, get_user, login, logout
from django.http import Http404
from rest_framework import status
from rest_framework.generics import CreateAPIView
from rest_framework.permissions import AllowAny, IsAdminUser, IsAuthenticated
from rest_framework.response import Response
from rest_framework.request import HttpRequest, Request
from rest_framework.views import APIView
from AccessSystem.admin import MyUser, Segment
from AccessSystem.serializers import PostSegmentSerializer, LoginSerializer, NewUserSerializer, SegmentSerializer, UserSerializer


class RegisterView(CreateAPIView):
    serializer_class = NewUserSerializer
    permission_classes = [AllowAny]
    queryset = MyUser.objects.all()

    def perform_create(self, serializer: NewUserSerializer):
        password = self.request.data.get('password')
        user = serializer.save()
        if password:
            user.set_password(password)
            user.save()
        user = authenticate(self.request, username=user.email, password=password)
        if user:
            return Response(
                {"message": f"Пользователь {user} зарегистрировался в системе."},
                status.HTTP_201_CREATED
            )
        else: return Response(
            {"error": f"Произошла ошибка при регистрации пользователя {user}."},
            status.HTTP_500_INTERNAL_SERVER_ERROR
        )

class LoginView(APIView):
    serializer_class = LoginSerializer
    permission_classes = [AllowAny]

    def post(self, request: HttpRequest):
        user = authenticate(
            request,
            email=request.data['email'],
            password=request.data['password'],
            access_token=request.headers['']
        )
        if user:
            if user.is_active:
                login(request, user)
                return Response({'message': f'Пользователь {user.email} вошёл в систему.'})
            else: return Response(
                {'message': f'Пользователь {request.data.get('email')} был деактивирован и удалён.'},
                status.HTTP_404_NOT_FOUND
            )
        else: return Response(
            {'message': f'Пользователь {request.data.get('email')} не зарегистрирован.'},
            status.HTTP_404_NOT_FOUND
        )

class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request: HttpRequest):
        user = request.user.email
        logout(request)
        try:
            return Response({'message': f'Пользователь {user} вышел из системы.'})
        except:
            return Response(
                {'message': f'Вы не вошли в систему.'},
                status.HTTP_401_UNAUTHORIZED
            )


class UserView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = UserSerializer

    def get_object(self, pk):
        try:
            return MyUser.objects.get(pk=pk)
        except Segment.DoesNotExist:
            raise Http404

    def get(self, request: Request):
        return Response(UserSerializer(request.user).data)

    def delete(self, request: Request):
        user = get_user(request)
        user.is_active = False
        user.save()
        # serializer = UserSerializer(user, data={'active_user': False}, partial=True)
        # if serializer.is_valid():
            # serializer.save()
        logout(request)
        return Response(status.HTTP_204_NO_CONTENT)
        # else:
        #     return Response(serializer.errors, status.HTTP_400_BAD_REQUEST)

    def patch(self, request: Request):
        user = request.user
        if 'password' in request.data:
            p_flag = True
            user.set_password(request.data['password'])
            user.save()
            if len(request.data) == 1:
                return Response(serializer.data, status.HTTP_200_OK)
        if 'name' in request.data:
            serializer = UserSerializer(
                user,
                data={'name': request.data['name']},
                partial=True
            )
        if 'surname' in request.data:
            serializer = UserSerializer(
                user,
                data={'surname': request.data['surname']},
                partial=True
            )
        if 'patronymic' in request.data:
            serializer = UserSerializer(
                user,
                data={'patronymic': request.data['patronymic']},
                partial=True
            )

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status.HTTP_400_BAD_REQUEST)


class SegmentView(APIView):
    permission_classes = [IsAuthenticated]

    def get_object(self, pk):
        try:
            return Segment.objects.get(pk=pk)
        except Segment.DoesNotExist:
            raise Http404

    def post(self, request: Request):
        serializer = PostSegmentSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(submiter=request.user)
            return Response(serializer.data, status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status.HTTP_400_BAD_REQUEST)

    def get(self, _, pk=None):
        if pk:
            serializer = SegmentSerializer(self.get_object(pk))
        else:
            serializer = SegmentSerializer(Segment.objects.all(), many=True)
        return Response(serializer.data)

    def patch(self, request: Request, pk):
        segment = self.get_object(pk)
        vote = -1 if int(request.data.pop('vote') == 0) else 1
        coef = 3 if 'AccessSystem.protect_segment' in request.user.get_group_permissions() else 1
        request.data['rating'] = segment.rating + vote * coef

        if 'is_protected' not in request.data:
            pass
        elif 'is_protected' in request.data \
        and request.data['is_protected'] != segment.is_protected \
        and 'AccessSystem.protect_segment' in request.user.get_group_permissions():
            serializer = SegmentSerializer(
                segment,
                data={'is_protected': request.data['is_protected']},
                partial=True
            )
        else: return Response(
                {'error': 'Рядовой пользователь не может замораживать сегменты. Это могут делать только модераторы или администраторы.'},
                status.HTTP_403_FORBIDDEN
            )

        serializer = SegmentSerializer(segment, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        else:
            return Response(serializer.errors, status.HTTP_400_BAD_REQUEST)

    def delete(self, request: Request, pk):
        if 'AccessSystem.delete_segment' not in request.user.get_group_permissions():
            return Response(
                {'error': 'Рядовой пользователь не может удалять сегменты, а только голосовать против. Удалять могут делать только модераторы или администраторы.'},
                status.HTTP_403_FORBIDDEN
            )
        segment = self.get_object(pk).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
