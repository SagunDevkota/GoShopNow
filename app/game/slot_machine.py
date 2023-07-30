import random

class SlotMachine:    
    def __init__(self,bet=10):
        self.bet = bet
        self.possible = [0,0,1,1,2,2,3,3,4,4,5]
        self.winning_bets = {
            "555":self.bet*800,
            "444":self.bet*100,
            "333":self.bet*50,
            "222":self.bet*30,
            "111":self.bet*10,
            "000":self.bet
        }

    def set_bet(self,bet):
        self.bet = bet

    def get_bet(self):
        return self.bet

    def play_game(self,reward_point):
        reward_point -= self.bet
        won = 0
        output = f"{random.choice(self.possible)}{random.choice(self.possible)}{random.choice(self.possible)}"
        if(output in self.winning_bets.keys()):
            reward_point += self.winning_bets[output]
            won = self.winning_bets[output]
        return {"output":output,"rewards_won":won,"new_reward_point":reward_point}
