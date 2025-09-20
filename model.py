# model.py
import math
import random
import pygame
from settings import ML_TRAIN_SAMPLES, ML_EPOCHS, ML_LR, WIDTH, HEIGHT

# вспомогательная функция — рэйкаст для подсчёта препятствий между двумя точками
def raycast_count_obstacles(p0, p1, obstacles, step=6):
    x0, y0 = p0
    x1, y1 = p1
    dx = x1 - x0
    dy = y1 - y0
    dist = math.hypot(dx, dy)
    if dist == 0:
        return 0
    steps = max(1, int(dist // step))
    count = 0
    for i in range(steps+1):
        t = i / steps
        x = x0 + dx * t
        y = y0 + dy * t
        for r in obstacles:
            if r.collidepoint((int(x), int(y))):
                count += 1
                # не считаем многократно один и тот же прямоугольник: но упрощаем — позволяем
                break
    return count

# логистическая регрессия на чистом питоне
class LogisticModel:
    def __init__(self, n_features=5):
        self.n = n_features
        # веса и bias
        self.w = [0.0 for _ in range(self.n)]
        self.b = 0.0

    @staticmethod
    def _sigmoid(z):
        # защита от переполнения
        if z >= 0:
            ez = math.exp(-z)
            return 1 / (1 + ez)
        else:
            ez = math.exp(z)
            return ez / (1 + ez)

    def predict_proba(self, x):
        # x: list of features length n
        z = self.b
        for i in range(self.n):
            z += self.w[i] * x[i]
        return self._sigmoid(z)

    def predict(self, x, thresh=0.5):
        return 1 if self.predict_proba(x) >= thresh else 0

    def train(self, X, Y, epochs=ML_EPOCHS, lr=ML_LR):
        # X: list of feature lists, Y: list 0/1
        m = len(X)
        for epoch in range(epochs):
            # batch gradient descent
            dw = [0.0]*self.n
            db = 0.0
            loss = 0.0
            for i in range(m):
                x = X[i]
                y = Y[i]
                p = self.predict_proba(x)
                err = p - y
                for j in range(self.n):
                    dw[j] += err * x[j]
                db += err
                # accumulating log loss
                # clip p
                p_clip = min(max(p, 1e-8), 1-1e-8)
                loss += -(y*math.log(p_clip) + (1-y)*math.log(1-p_clip))
            # update
            for j in range(self.n):
                self.w[j] -= lr * (dw[j] / m)
            self.b -= lr * (db / m)
            # optional: small print every 50 epochs
            if (epoch+1) % 50 == 0:
                avg_loss = loss / m
                # print(f"[ML] epoch {epoch+1}/{epochs}, loss={avg_loss:.4f}")

    # Конструируем датасет, обучаем на текущей карте (obstacles)
    def train_on_map(self, obstacles, grid_w, grid_h, samples=ML_TRAIN_SAMPLES):
        X = []
        Y = []
        max_dist = math.hypot(WIDTH, HEIGHT)
        for _ in range(samples):
            # сэмплим позиции, которые не внутри препятствия
            while True:
                bx = random.randint(0, WIDTH-1)
                by = random.randint(0, HEIGHT-1)
                # если внутри obstacle, сэмплим заново
                inside = False
                for r in obstacles:
                    if r.collidepoint((bx, by)):
                        inside = True
                        break
                if not inside:
                    break
            while True:
                px = random.randint(0, WIDTH-1)
                py = random.randint(0, HEIGHT-1)
                inside = False
                for r in obstacles:
                    if r.collidepoint((px, py)):
                        inside = True
                        break
                if not inside:
                    break
            dx = (px - bx) / WIDTH
            dy = (py - by) / HEIGHT
            dist = math.hypot(px - bx, py - by) / max_dist
            # line of sight: есть ли прямой проход без препятствий
            count_obs = raycast_count_obstacles((bx, by), (px, py), obstacles)
            los = 1 if count_obs == 0 else 0
            obst_norm = min(count_obs / 6.0, 1.0)
            features = [dx, dy, dist, los, obst_norm]
            # label: используем простую "правильную" стратегию для генерации меток:
            # стрелять, если есть LOS и расстояние < 0.45 (практически демонстрация)
            label = 1 if (los == 1 and dist < 0.45) else 0
            X.append(features)
            Y.append(label)
        # тренируем модель
        self.train(X, Y)
        # возвращаем обученные веса для отладки
        return self.w, self.b
