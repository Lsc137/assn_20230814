import tkinter as tk
import random

# --- 상수 설정 ---
WIDTH = 400
HEIGHT = 600
GRAVITY = 0.6
JUMP_STRENGTH = -10
GAME_SPEED_MS = 20
PIPE_SPEED = 5
PIPE_GAP = 150
PIPE_WIDTH = 60
PIPE_SPAWN_MS = 1500

class FlappyBirdGame:
    def __init__(self, root):
        self.root = root
        self.root.title("Tkinter Flappy Bird")
        self.root.geometry(f"{WIDTH}x{HEIGHT}")
        self.root.resizable(False, False)

        # 게임 캔버스 설정
        self.canvas = tk.Canvas(root, width=WIDTH, height=HEIGHT, bg="sky blue")
        self.canvas.pack()

        # 점수 레이블
        self.score = 0
        self.score_label = tk.Label(root, text=f"Score: {self.score}", font=("Arial", 20), bg="sky blue")
        self.score_label.place(x=10, y=10)

        # 게임 변수 초기화
        self.bird_y = HEIGHT // 2
        self.velocity = 0
        self.game_over = False
        self.pipe_pairs = []
        
        # [추가] 파이프 생성 타이머의 ID를 저장할 변수
        self.pipe_timer = None 

        self.bird = self.canvas.create_oval(
            WIDTH // 4 - 15, self.bird_y - 15,
            WIDTH // 4 + 15, self.bird_y + 15,
            fill="yellow", outline="black"
        )

        # 스페이스바 입력 바인딩
        self.canvas.bind_all("<space>", self.jump)
        self.canvas.bind_all("<Button-1>", self.jump)

        #게임 시작
        self.start_game()

    def start_game(self):
        """게임을 시작하고 루프를 실행합니다."""
        self.game_loop()
        self.create_pipe()

    def jump(self, event):
        """새가 점프하도록 속도를 변경합니다."""
        if not self.game_over:
            self.velocity = JUMP_STRENGTH

    def game_loop(self):
        """메인 게임 루프: 새 이동, 파이프 이동, 충돌 검사"""
        if self.game_over:
            return

        # 1. 새 이동 (중력 적용)
        self.velocity += GRAVITY
        self.canvas.move(self.bird, 0, self.velocity)
        
        # 2. 파이프 이동 및 관리
        new_pipe_pairs = []
        scored = False

        for top_pipe, bottom_pipe, passed in self.pipe_pairs:
            self.canvas.move(top_pipe, -PIPE_SPEED, 0)
            self.canvas.move(bottom_pipe, -PIPE_SPEED, 0)

            pipe_coords = self.canvas.coords(top_pipe)
            
            if pipe_coords and pipe_coords[2] < 0: 
                self.canvas.delete(top_pipe)
                self.canvas.delete(bottom_pipe)
            else:
                # 점수 획득 확인
                bird_coords = self.canvas.coords(self.bird)
                if not passed and pipe_coords[2] < bird_coords[0]: # 파이프의 오른쪽 끝이 새의 왼쪽 끝을 지났을 때
                    passed = True
                    if not scored:
                        self.score += 1
                        self.score_label.config(text=f"Score: {self.score}")
                        scored = True

                new_pipe_pairs.append((top_pipe, bottom_pipe, passed))

        self.pipe_pairs = new_pipe_pairs

        # 3. 충돌 검사
        self.check_collisions()

        # 4. 다음 게임 루프 예약
        self.root.after(GAME_SPEED_MS, self.game_loop)

    def create_pipe(self):
        """일정 시간마다 새 파이프 쌍을 생성합니다."""
        if self.game_over:
            return

        # 파이프 틈의 Y 위치를 랜덤하게 설정
        gap_y = random.randint(PIPE_GAP, HEIGHT - PIPE_GAP)
        
        # 상단 파이프
        top_pipe = self.canvas.create_rectangle(
            WIDTH, 0, 
            WIDTH + PIPE_WIDTH, gap_y - PIPE_GAP // 2,
            fill="green", outline="black"
        )
        
        # 하단 파이프
        bottom_pipe = self.canvas.create_rectangle(
            WIDTH, gap_y + PIPE_GAP // 2,
            WIDTH + PIPE_WIDTH, HEIGHT,
            fill="green", outline="black"
        )

        # 파이프 리스트에 추가 (점수 획득 여부 'False'로)
        self.pipe_pairs.append((top_pipe, bottom_pipe, False))

        #삭제를 위해 타이머를 저장
        self.pipe_timer = self.root.after(PIPE_SPAWN_MS, self.create_pipe)

    def check_collisions(self):
        """새가 파이프나 경계에 부딪혔는지 검사합니다."""
        bird_coords = self.canvas.coords(self.bird)
        
        if not bird_coords: 
            return

        if bird_coords[1] <= 0 or bird_coords[3] >= HEIGHT:
            self.end_game()
            return

        # 2. 파이프 충돌 (find_overlapping 사용)
        colliders = self.canvas.find_overlapping(*bird_coords)

        for item in colliders:
            if item != self.bird:
                self.end_game()
                return

    def end_game(self):
        """게임 오버 처리를 합니다."""
        if self.game_over:
            return
            
        self.game_over = True
        
        self.canvas.create_text(
            WIDTH // 2, HEIGHT // 2 - 40,
            text="GAME OVER",
            font=("Arial", 40, "bold"),
            fill="black",
            tags="gameover" # 텍스트에도 태그를 달아 쉽게 지울 수 있게 함
        )
        
        self.restart_button = tk.Button(
            self.root, 
            text="Restart", 
            font=("Arial", 20), 
            command=self.restart_game
        )
        
        self.restart_button.place(
            x=WIDTH // 2, 
            y=HEIGHT // 2 + 30, 
            anchor="center"
        )
        
        print(f"Final Score: {self.score}")

    def restart_game(self):
        """게임을 초기 상태로 리셋하고 다시 시작합니다."""
        
        # [추가] 재시작 시, 예약되어 있던 이전 게임의 파이프 생성 타이머를 취소
        if self.pipe_timer:
            self.root.after_cancel(self.pipe_timer)
            self.pipe_timer = None # 타이머 변수 초기화
        
        # 1. 게임 상태 변수 초기화
        self.game_over = False
        self.score = 0
        self.bird_y = HEIGHT // 2
        self.velocity = 0
        self.pipe_pairs = []

        # 2. GUI 요소 리셋
        self.score_label.config(text=f"Score: {self.score}")
        self.canvas.delete("all") # 캔버스의 모든 그림 (새, 파이프, 텍스트) 삭제
        self.restart_button.destroy() # 재시작 버튼 위젯 자체를 파괴

        # 3. 새 다시 만들기 (원으로)
        self.bird = self.canvas.create_oval(
            WIDTH // 4 - 15, self.bird_y - 15,
            WIDTH // 4 + 15, self.bird_y + 15,
            fill="yellow", outline="black"
        )

        # 4. 게임 루프 다시 시작
        self.start_game()

# --- 메인 코드 ---
if __name__ == "__main__":
    root = tk.Tk()
    app = FlappyBirdGame(root)
    root.mainloop()