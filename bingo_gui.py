import random as rd
import tkinter as tk

ROWS = 7
COLUMNS = 11
BINGO_MAX = 75
FONT_SIZE = 80

class App(tk.Tk):
    
    def __init__(self):
        super().__init__()
        
        # ビンゴの数列を初期化
        self.bingo_nums = list(x for x in range(1, BINGO_MAX + 1))
        
        # メインウィンドウの最小サイズを指定
        self.minsize(1280, 900)
        
        # メインウィンドウの設定
        self.title("BINGO")
        
        # ウィジェット作成
        self.create_widgets()
        

    def create_widgets(self):
        """ウィジェットを作成する
        
        グリッドを使用
        - 取り出した数字表示部
        - 取り出した数字の履歴表示部
        - 数字取り出しボタン
        """

        # グリッドを設定
        for x in range(0, ROWS):
            self.rowconfigure(index=x)
            
        for X in range(0, COLUMNS):
            self.columnconfigure(index=x)

        # ラベルの配置
        for num in range(1, BINGO_MAX + 1):
            if num > BINGO_MAX or num == 0:
                break
            tk.Label(self.master, text=str(num), foreground='#888888', font=(None, FONT_SIZE)).grid(row=self.get_row_num(num), column=self.get_column_num(num))

        # 取り出した数字を表示するウィジェット
        self.current_num = tk.StringVar(value="BINGO")
        self.label = tk.Label(self.master, textvariable=self.current_num, justify="center", width=8, font=(None, FONT_SIZE * 2)).grid(row=0, column=0, rowspan=2)

        # ボタンウィジェットをメインウィンドウに配置、イベントを登録S
        self.button_label = tk.StringVar(value="START")
        self.button = tk.Button(self.master, textvariable=self.button_label, command=self.button_event, font=(None, FONT_SIZE))
        self.button.grid(row=ROWS - 1, column=0, rowspan=2)

    
    def button_event(self):
        """イベントハンドラ\
            
        ビンゴの残数字リストからランダムに１つの数字を取り出しラベルに表示、履歴に追加する
        エラー発生時、ラベルに `ERROR` 表示
        
        """
        
        try:
            # 番号を取り出す
            num = self.draw_num()
            self.current_num.set(str(num))
            self.change_color(num)
            self.change_button_state()    
            
        except Exception as e:
            print(e)
            self.current_num.set("ERROR")
            
            
    def draw_num(self):
        """ビンゴの残数字リストからランダムに数字を取り出す
        
        Returns:
            int: 取り出した数字
        Raises:
            Exception: 発生した例外
        """
        
        try:
            return self.bingo_nums.pop(rd.randint(0, len(self.bingo_nums) - 1))
        except Exception as e:
            print(e)
            raise Exception("数字の取り出し時に例外発生") from e
    
    
    def change_button_state(self):
        """ボタンの状態を変化させる
        
        ビンゴの残数字リストが空になった場合:
            ラベル: ”END”
            状態: "disable"
        
        その他の場合:
            ラベル: ”NEXT”
        """
        
        if len(self.bingo_nums) == 0:
            self.button_label.set("END")
            self.button["state"] = "disable"
        else:
            self.button_label.set("NEXT")
    
    
    def get_row_num(self, num) -> int:
        """グリッドの行番号を取得する
        
        Returns:
            int: 行番号
        """
        
        tens_digit = num // 10
        ones_digit = num % 10
        return tens_digit - 1 if ones_digit == 0 else tens_digit
    
    
    def get_column_num(self, num) -> int:
        """グリッドの列番号を取得する
        
        Returns:
            int: 列番号
        """
        ones_digit = num % 10
        return 10 if ones_digit == 0 else ones_digit
    
    
    def change_color(self, num):
        """取り出した数字の履歴表示色を変更する
        
        グレーから黒または白（OSのテーマ色に依存）へ変更
        
        Raises:
            Exception: 発生した例外
        """
        
        try:
            tk.Label(self.master, text=str(num), foreground=None, font=(None, FONT_SIZE)).grid(row=self.get_row_num(num), column=self.get_column_num(num))
            
        except Exception as e:
            print(e)
            raise Exception("色変更時に例外発生") from e


def main():
    root = App()
    root.mainloop()


if __name__ == "__main__":
    main()
