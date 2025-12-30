# 強化學習專題報告：AI 自動化飛機射擊遊戲

## 1. 專題目的 (Project Objective)
本專題的主要目的是利用強化學習（Reinforcement Learning）技術，訓練一個Agent來自動遊玩一款 2D 飛機射擊遊戲。
目標是讓 AI 能夠在充滿敵機與彈幕的環境中：
1.  **學會生存**：透過辨識危險（子彈）並進行閃躲，最大化存活時間。
2.  **學會攻擊**：在確保安全的前提下，移動到有利位置擊落敵機以獲取高分。
3.  **自主決策**：不依賴人為編寫的固定規則（Rule-based），而是透過與環境的互動自行學習最佳策略。

## 2. 強化學習五大要素 (RL Components)

### (1) 環境 (Environment)
*   **定義**：由 `pygame` 建構的遊戲世界（視窗大小 $1280 \times 720$）。
*   **內容**：包含我方飛機、5 架敵方飛機（會左右移動與發射子彈）、敵方子彈以及我方子彈。
*   **互動方式**：環境會根據 Agent 的動作更新畫面（下一幀），並回傳新的狀態與獎勵。

### (2) 代理人 (Agent)
*   **定義**：玩家控制的飛機（`airplane_rect`）。
*   **角色**：它擁有一個大腦（Q-Table），負責觀察環境狀態並做出決策（移動或射擊）。
*   **機制**：採用 Frame Skipping 機制，每 4 幀（Frame）進行一次決策與學習，以穩定訓練效果並讓動作產生位移。

### (3) 狀態 (State)
為了降低運算複雜度，程式將連續的遊戲畫面簡化（Discretization）為 3 個離散特徵的組合，由 `get_rl_state` 函式定義：
1.  **最近敵人的相對位置** (3種)：
    *   大致對齊 (Align)
    *   在左邊 (Left)
    *   在右邊 (Right)
2.  **子彈威脅感知** (4種)：
    *   安全 (Safe)
    *   左側有子彈逼近 (Left Danger)
    *   中間有子彈逼近 (Center Danger)
    *   右側有子彈逼近 (Right Danger)
3.  **自身位置** (3種)：
    *   左區 (Left)
    *   中區 (Center)
    *   右區 (Right) — *防止 AI 卡在牆角*

*   **總狀態數**：3 X 4 X 3 = 36 種狀態。

### (4) 動作 (Action)
Agent 可以執行的 6 種離散動作：
*   `0`: **停止 (STOP)** - 保持原地不動。
*   `1`: **向左移 (LEFT)**。
*   `2`: **向右移 (RIGHT)**。
*   `3`: **向上移 (UP)**。
*   `4`: **向下移 (DOWN)**。
*   `5`: **射擊 (FIRE)** - 具有冷卻時間（40幀）限制。

### (5) 獎勵 (Reward)
獎勵機制的設計引導了 AI 的行為模式（保命優先，其次得分）：
*   **存活獎勵**：`+1` (每存活一個決策週期)。
*   **擊殺獎勵**：`+10` (當分數增加時，鼓勵攻擊)。
*   **受傷懲罰**：`-200` (當生命值減少時，給予極大懲罰，強迫 AI 學習閃躲)。

## 3. 使用的演算法 (Algorithm)

本專題使用 **Q-Learning (Q-Table)** 演算法。

*   **類型**：這是一種無模型（Model-Free）、基於價值（Value-Based）的強化學習演算法。
*   **核心機制**：
    *   **Q-Table**：建立一個表格來記錄在特定「狀態」下採取特定「動作」的預期價值（Q-Value）。
    *   **更新公式**：
        $$Q(S, A) \leftarrow Q(S, A) + \alpha [R + \gamma \max Q(S', A') - Q(S, A)]$$
        *   $\alpha$ (Learning Rate): 0.1 (學習率)
        *   $\gamma$ (Gamma): 0.9 (折扣因子，重視未來獎勵)
    *   **探索策略 (Epsilon-Greedy)**：
        *   設定 `epsilon` (探索率) 初始為 0.5，隨著訓練局數增加逐漸衰減至 0.01。
        *   前期多隨機嘗試（探索），後期根據 Q-Table 選擇最佳動作（利用）。

## 4. 功能特點
*   **自動存檔**：訓練過程中的 Q-Table 會自動儲存為 `q_table_v2.pkl`，下次執行時自動讀取。
*   **視覺化除錯**：按下 `P` 鍵或程式結束時，會印出目前的 Q-Table 內容，方便觀察 AI 的學習狀況。
*   **中斷保護**：支援 `Ctrl+C` 中斷訓練並自動存檔。

## 5. 訓練成果範例 (Training Results Example)

以下是 AI 訓練後的 Q-Table 視覺化輸出範例。這代表 AI 在不同狀態下對各個動作的評分（Q-Value），分數越高代表該動作越好。

**範例解讀：**
1.  **攻擊策略**：當敵人對齊且環境安全時 (`Enemy:Align | Danger:Safe`)，AI 選擇 **FIRE** (分數 51.64) 作為最佳動作。
2.  **閃避策略**：當左邊有危險時 (`Danger:L-Danger`)，AI 選擇 **RIGHT** (向右移) 並給予 **LEFT** (向左移) 極低或負分。

```text
=== Q-Table Visualization ===
State [Enemy:Align | Danger:Safe     | Pos:Left  ]:
  STOP :    44.11
  LEFT :    44.37
  RIGHT:    29.17
  UP   :    45.09
  DOWN :    44.09
  FIRE :    51.64 <--- BEST
State [Enemy:Align | Danger:Safe     | Pos:Center]:
  STOP :    44.92
  LEFT :    44.39
  RIGHT:    44.92
  UP   :    45.20
  DOWN :    44.93
  FIRE :    46.50 <--- BEST
State [Enemy:Align | Danger:Safe     | Pos:Right ]:
  STOP :    42.74
  LEFT :    41.35
  RIGHT:    36.32
  UP   :    44.44
  DOWN :    44.57
  FIRE :    45.78 <--- BEST
State [Enemy:Align | Danger:L-Danger | Pos:Left  ]:
  STOP :    17.83
  LEFT :   -10.26
  RIGHT:    45.08 <--- BEST
  UP   :    19.45
  DOWN :    15.36
  FIRE :     5.41
State [Enemy:Align | Danger:L-Danger | Pos:Center]:
  STOP :    18.30
  LEFT :    15.84
  RIGHT:    37.13 <--- BEST
  UP   :    17.37
  DOWN :    20.93
  FIRE :    20.34
State [Enemy:Align | Danger:L-Danger | Pos:Right ]:
  STOP :    28.84 <--- BEST
  LEFT :    -4.92
  RIGHT:     1.03
  UP   :     2.67
  DOWN :     5.90
  FIRE :    -0.42
State [Enemy:Align | Danger:C-Danger | Pos:Left  ]:
  STOP :    -3.11
  LEFT :    39.91 <--- BEST
  RIGHT:     5.01
  UP   :     7.52
  DOWN :     5.26
  FIRE :     6.13
State [Enemy:Align | Danger:C-Danger | Pos:Center]:
  STOP :    14.65
  LEFT :    14.93
  RIGHT:    29.71 <--- BEST
  UP   :    16.50
  DOWN :    14.72
  FIRE :    17.18
State [Enemy:Align | Danger:C-Danger | Pos:Right ]:
  STOP :     2.74
  LEFT :    28.40 <--- BEST
  RIGHT:   -19.34
  UP   :    -8.14
State [Enemy:Align | Danger:R-Danger | Pos:Left  ]:
  STOP :     2.16
  LEFT :     1.03
  RIGHT:     4.11
  UP   :     2.98
  DOWN :    47.48 <--- BEST
  FIRE :    -2.71
State [Enemy:Align | Danger:R-Danger | Pos:Center]:
  STOP :    18.60
  LEFT :    44.44 <--- BEST
  RIGHT:    11.58
  UP   :    13.66
  DOWN :    15.39
  FIRE :    18.78
State [Enemy:Align | Danger:R-Danger | Pos:Right ]:
  STOP :     1.20
  LEFT :    45.88 <--- BEST
  RIGHT:   -15.69
  UP   :    12.32
  DOWN :     5.70
  FIRE :    18.46
State [Enemy:Left  | Danger:Safe     | Pos:Left  ]:
  STOP :    44.10
  LEFT :    44.07
  RIGHT:    30.23
  UP   :    48.01 <--- BEST
  DOWN :    43.73
  FIRE :    43.89
State [Enemy:Left  | Danger:Safe     | Pos:Center]:
  STOP :    43.02 <--- BEST
  LEFT :    40.31
  RIGHT:    41.39
  UP   :    41.96
  DOWN :    39.74
  FIRE :    42.05
State [Enemy:Left  | Danger:Safe     | Pos:Right ]:
  STOP :    44.01
  LEFT :    42.32
  RIGHT:    42.39
  UP   :    45.59 <--- BEST
  DOWN :    44.01
  FIRE :    42.59
State [Enemy:Left  | Danger:L-Danger | Pos:Left  ]:
  STOP :     5.81
  LEFT :   -10.59
  RIGHT:    43.56 <--- BEST
  UP   :     0.22
  DOWN :    13.24
  FIRE :    13.19
State [Enemy:Left  | Danger:L-Danger | Pos:Center]:
  STOP :   -13.00
  LEFT :    -6.00
  RIGHT:    37.28 <--- BEST
  UP   :   -10.15
  DOWN :   -18.00
  FIRE :   -15.04
State [Enemy:Left  | Danger:L-Danger | Pos:Right ]:
  STOP :   -18.63
  LEFT :     1.56 <--- BEST
  RIGHT:   -14.97
  UP   :    -8.87
  DOWN :   -11.91
  FIRE :   -12.88
State [Enemy:Left  | Danger:C-Danger | Pos:Left  ]:
  LEFT :    43.15 <--- BEST
  RIGHT:     4.80
  UP   :   -12.31
State [Enemy:Left  | Danger:C-Danger | Pos:Center]:
  STOP :     6.10
  LEFT :    35.44 <--- BEST
  RIGHT:   -11.51
  UP   :    11.50
  DOWN :    -1.64
  FIRE :    11.28
State [Enemy:Left  | Danger:C-Danger | Pos:Right ]:
  STOP :    -6.12
  LEFT :    -9.92
  RIGHT:     2.18
  UP   :   -10.75
  DOWN :    -4.66
  FIRE :    34.65 <--- BEST
State [Enemy:Left  | Danger:R-Danger | Pos:Left  ]:
  STOP :     6.53
  LEFT :    45.51 <--- BEST
  RIGHT:     9.97
  UP   :    -0.75
  DOWN :     3.79
  FIRE :    10.43
State [Enemy:Left  | Danger:R-Danger | Pos:Center]:
  STOP :    -3.21
  LEFT :     0.07
  RIGHT:   -10.49
  UP   :    -7.41
  DOWN :    18.89 <--- BEST
  FIRE :    -9.08
State [Enemy:Left  | Danger:R-Danger | Pos:Right ]:
  STOP :     2.20
  LEFT :    43.33 <--- BEST
  RIGHT:    -6.84
  UP   :     4.47
  DOWN :     3.52
  FIRE :    -0.84
State [Enemy:Right | Danger:Safe     | Pos:Left  ]:
  STOP :    43.58
  LEFT :    30.44
  RIGHT:    43.19
  UP   :    43.26
  DOWN :    43.55
  FIRE :    47.09 <--- BEST
State [Enemy:Right | Danger:Safe     | Pos:Center]:
  STOP :    43.14
  LEFT :    42.22
  RIGHT:    44.44 <--- BEST
  UP   :    43.15
  DOWN :    43.15
  FIRE :    43.16
State [Enemy:Right | Danger:Safe     | Pos:Right ]:
  STOP :    44.46
  LEFT :    33.07
  RIGHT:    45.97 <--- BEST
  UP   :    44.45
  DOWN :    44.45
  FIRE :    44.44
State [Enemy:Right | Danger:L-Danger | Pos:Left  ]:
  STOP :     2.48
  LEFT :    -1.59
  RIGHT:    43.54 <--- BEST
  UP   :     2.44
  DOWN :    -1.92
  FIRE :     1.24
State [Enemy:Right | Danger:L-Danger | Pos:Center]:
  STOP :     6.89
  LEFT :    15.67
  RIGHT:    45.30 <--- BEST
  UP   :     8.66
  DOWN :    13.67
  FIRE :     9.69
State [Enemy:Right | Danger:L-Danger | Pos:Right ]:
  STOP :    18.92
  LEFT :    13.93
  RIGHT:    39.22 <--- BEST
  UP   :    17.68
  DOWN :    18.82
  FIRE :     9.94
State [Enemy:Right | Danger:C-Danger | Pos:Left  ]:
  STOP :     7.55
  LEFT :     6.83
  RIGHT:    18.60
  UP   :    12.99
  DOWN :     8.07
  FIRE :    43.45 <--- BEST
State [Enemy:Right | Danger:C-Danger | Pos:Center]:
  STOP :    20.35
  LEFT :    23.59
  RIGHT:    12.95
  UP   :    23.92
  DOWN :    21.84
  FIRE :    41.70 <--- BEST
State [Enemy:Right | Danger:C-Danger | Pos:Right ]:
  RIGHT:    35.71 <--- BEST
  UP   :     0.47
  DOWN :     0.80
  FIRE :     4.21
State [Enemy:Right | Danger:R-Danger | Pos:Left  ]:
  STOP :   -14.17
  LEFT :    -8.71
  RIGHT:    22.76 <--- BEST
  UP   :   -17.95
  DOWN :   -14.16
  FIRE :   -11.95
State [Enemy:Right | Danger:R-Danger | Pos:Center]:
  STOP :    14.27
  LEFT :    35.14 <--- BEST
  RIGHT:    15.28
  UP   :    10.55
  DOWN :     4.38
  FIRE :    12.14
State [Enemy:Right | Danger:R-Danger | Pos:Right ]:
  STOP :     4.41
  LEFT :    40.51 <--- BEST
  RIGHT:     9.69
  UP   :     1.48
  DOWN :     3.86
  FIRE :     4.32
=============================
```
