"""コンソール版BINGO抽選機。"""

import random as rd

def main():
    """Enterキーを受け付けながら、重複なしで番号を抽選する。"""
    # ビンゴの数列を初期化
    nums = list(x for x in range(1, 76))
    
    # 抽選開始
    print("ビンゴを開始！")
    print("Enterキーを入力して次の番号を抽選する")
    
    while len(nums) > 0:
        input()
        num = nums.pop(rd.randint(0, len(nums) - 1))
        print(num)
        

if __name__ == '__main__':
    main()
