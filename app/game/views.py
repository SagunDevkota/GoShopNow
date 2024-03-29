"""Viewset for slotmachine game."""
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.response import Response

from drf_spectacular.utils import extend_schema
from drf_spectacular.openapi import OpenApiParameter

from django.http import HttpResponse

from core.models import DiscountCoupon
from game.slot_machine import SlotMachine

import uuid

class SlotMachineViewSet(APIView):
    """API view for SlotMachine."""
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    slot_machine = SlotMachine()
    serializer_class = None

    @extend_schema(
            parameters=[OpenApiParameter(name="bet",location=OpenApiParameter.QUERY, description='Bet', required=False, type=str)]
    )
    def get(self,request,format=None):
        """
        View for slotmachine.<br>
        Valid bets = [10,50,100]
        Winning Bets:{<br>
            "555":bet_amount*800,<br>
            "444":bet_amount*100,<br>
            "333":bet_amount*50,<br>
            "222":bet_amount*30,<br>
            "111":bet_amount*10,<br>
            "000":bet_amount<br>
        }
        """
        if("bet" in request.query_params.keys()):
            if(request.query_params.get("bet") in ['10','50','100']):
                self.slot_machine.set_bet(int(request.query_params["bet"]))
            else:
                return Response({"error":"Invalid Bet"},status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({"error":"Bet not found"},status=status.HTTP_428_PRECONDITION_REQUIRED)
        if(request.user.reward_points >= self.slot_machine.get_bet()):
            response = self.slot_machine.play_game(request.user.reward_points)
            request.user.reward_points = response["new_reward_point"]
            request.user.save()
            if(response["rewards_won"] > 0):
                DiscountCoupon.objects.create(user=self.request.user,
                                                    coupon_code=str(uuid.uuid4())[:6],
                                                    max_amount=response["rewards_won"],
                                                    max_percentage=self.slot_machine.get_bet()/5)
            return Response({"response":response})
        else:
            return Response({"error":"Insufficient Reward Points"},status=status.HTTP_400_BAD_REQUEST)
