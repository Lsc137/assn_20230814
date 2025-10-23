import tkinter as tk
import random

# --- 상수 설정 ---
WIDTH = 400         # 창 너비
HEIGHT = 600        # 창 높이
GRAVITY = 0.6       # 중력
JUMP_STRENGTH = -10 # 점프 시 속도
GAME_SPEED_MS = 20  # 게임 루프 간격 (밀리초)
PIPE_SPEED = 5      # 파이프 이동 속도
PIPE_GAP = 150      # 파이프 사이 간격
PIPE_WIDTH = 60     # 파이프 너비
PIPE_SPAWN_MS = 1500 # 파이프 생성 간격 (밀리초)

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
        self.pipe_pairs = [] # (top_pipe, bottom_pipe, passed)

        # 새 만들기 (간단한 사각형)
        self.bird = self.canvas.create_rectangle(
            WIDTH // 4 - 15, self.bird_y - 15,
            WIDTH // 4 + 15, self.bird_y + 15,
            fill="yellow", outline="black"
        )

        # 스페이스바 입력 바인딩
        self.canvas.bind_all("<space>", self.jump)
        self.canvas.bind_all("<Button-1>", self.jump) # 마우스 클릭으로도 점프

        # 게임 시작
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
        scored = False # 한 프레임에 중복 점수 방지

        for top_pipe, bottom_pipe, passed in self.pipe_pairs:
            self.canvas.move(top_pipe, -PIPE_SPEED, 0)
            self.canvas.move(bottom_pipe, -PIPE_SPEED, 0)

            pipe_coords = self.canvas.coords(top_pipe)
            
            # 파이프가 화면 밖으로 나갔는지 확인
            if pipe_coords[2] < 0: # (x1, y1, x2, y2) -> x2가 0보다 작으면
                self.canvas.delete(top_pipe)
                self.canvas.delete(bottom_pipe)
            else:
                # 점수 획득 확인
                bird_coords = self.canvas.coords(self.bird)
                if not passed and pipe_coords[2] < bird_coords[0]: # 파이프의 오른쪽 끝이 새의 왼쪽 끝을 지났을 때
                    passed = True
                    if not scored: # 이 프레임에서 아직 점수를 얻지 않았다면
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

        # 다음 파이프 생성 예약
        self.root.after(PIPE_SPAWN_MS, self.create_pipe)

    def check_collisions(self):
        """새가 파이프나 경계에 부딪혔는지 검사합니다."""
        bird_coords = self.canvas.coords(self.bird)
        
        # 1. 화면 상단/하단 경계 충돌
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
            WIDTH // 2, HEIGHT // 2,
            text="GAME OVER",
            font=("Arial", 40, "bold"),
            fill="black"
        )
        print(f"Final Score: {self.score}")

# --- 메인 코드 ---
if __name__ == "__main__":
    root = tk.Tk()
    app = FlappyBirdGame(root)
    root.mainloop()