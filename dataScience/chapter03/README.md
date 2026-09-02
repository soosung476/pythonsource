# Chapter 03 — Gradio로 만드는 데이터 앱 정리

Chapter01(크롤링·파일 입출력), Chapter02(pandas·matplotlib·seaborn·Oracle)에서 만든 결과물을
**웹 화면으로 꺼내 보여주는** 단계. 파이썬 함수 하나를 그대로 웹 UI로 바꿔주는 `gradio`를 다룬다.

- 환경: macOS(M4), `.venv`, Gradio 6.26.0 / matplotlib 3.11.1
- 한글 폰트: `mpl.rc('font', family='AppleGothic')` + `mpl.rc('axes', unicode_minus=False)`
- 비밀값: `.env` + `python-dotenv` (`ORACLE_USER` / `ORACLE_PASSWORD` / `ORACLE_DSN` / `GEMINI_API_KEY`)

---

## 1. 핵심 개념 한 장 요약

### Gradio의 기본 사고방식

```
함수(fn)  →  입력 컴포넌트(inputs)  →  출력 컴포넌트(outputs)
```

만들어 둔 파이썬 함수의 **매개변수 = 입력창**, **return 값 = 출력창**이다.
따라서 `return`의 **개수와 순서**가 `outputs` 리스트의 개수·순서와 반드시 일치해야 한다.

### Interface vs Blocks

| | `gr.Interface` | `gr.Blocks` |
|---|---|---|
| 배치 | 자동 (입력 왼쪽 / 출력 오른쪽) | 직접 설계 (`gr.Row`, `gr.Column`) |
| 실행 시점 | 값이 바뀌거나 Submit | 이벤트로 지정 (`btn.click(...)`) |
| 쓸 때 | 함수 하나짜리 데모 | 대시보드처럼 화면 구성이 필요할 때 |

```python
# Interface — 자동 배치
demo = gr.Interface(fn=함수, inputs=[...], outputs=[...], title="...")

# Blocks — 직접 배치 + 이벤트 연결
with gr.Blocks(title="...") as demo:
    with gr.Row():
        a = gr.Number(label="키(cm)")
    btn = gr.Button("계산하기")
    out = gr.Textbox(label="결과")
    btn.click(fn=함수, inputs=[a], outputs=[out])
```

### 실행 / 종료

```python
demo.launch()   # 로컬 서버 기동 (노트북 안에 화면이 뜸)
demo.close()    # 포트 반납 — 다음 셀 실행 전에 꼭 닫아줄 것
```

> 노트북에서 `close()` 없이 계속 `launch()` 하면 포트가 하나씩 늘어난다. 예제마다 마지막 셀이 `demo.close()`인 이유.

---

## 2. 컴포넌트 정리 (예제에서 실제로 쓴 것)

| 컴포넌트 | 용도 | 등장 |
|---|---|---|
| `gr.Textbox(label, placeholder, lines)` | 문자열 입·출력 | ex01·ex02 |
| `gr.Number(label)` | 숫자 입·출력 | ex03·ex07·ex08 |
| `gr.Dropdown([선택지], label)` | 목록 중 하나 선택 | ex03·ex05·ex07·ex10 |
| `gr.Radio([선택지], label)` | 라디오 버튼 (Dropdown 대체) | ex03 주석 |
| `gr.Slider(minimum, maximum, step, label)` | 범위 값 조절 | ex05 |
| `gr.Image(label)` | 이미지 업로드/표시 (numpy 배열로 들어옴) | ex04 |
| `gr.File(label, file_types)` | 파일 업로드 | ex09 |
| `gr.Dataframe(label)` | pandas DataFrame을 표로 출력 | ex09·ex10 |
| `gr.Plot(label)` | matplotlib `fig` 객체를 그래프로 출력 | ex09·ex10 |
| `gr.Button("...")` | 클릭 이벤트 트리거 | ex08·ex10 |
| `gr.Markdown("...")` | 화면에 설명 텍스트 | ex08·ex10 |
| `gr.ChatInterface(fn)` | 채팅 UI (`fn(message, history)`) | ex06 |

`inputs`/`outputs`에 `"text"`, `"number"` 같은 **문자열 축약**도 되지만(ex01),
`label`을 붙이려면 컴포넌트 객체를 써야 한다.

---

## 3. 예제별 정리

### ex01 — hello gradio
가장 작은 형태. `fn` / `inputs` / `outputs` / `title` / `description` 5개만으로 웹앱이 뜬다.
`inputs="text"`를 `"number"`로 바꾸면 입력창 모양이 바뀌는 것을 확인.

### ex02 — 텍스트 변환기 (출력 여러 개)
`outputs`에 **리스트**를 넘기면 출력창이 여러 개 생긴다.
함수는 `return upper, lower, reversed, length`처럼 튜플로 반환.

```python
return sentence.upper(), sentence.lower(), sentence[::-1], len(sentence)
```
- 문자열 뒤집기: 슬라이싱 `sentence[::-1]`

### ex03 — 숫자 계산기 (입력 여러 개 + 선택지)
`inputs` 리스트의 **순서**가 함수 매개변수 순서와 일치.
0으로 나누는 경우처럼 **예외 상황은 함수 안에서 문자열로 먼저 return**해 막는다.

### ex04 — 이미지 흑백 변환
`gr.Image`는 업로드 이미지를 `(높이, 너비, 채널)` numpy 배열로 넘겨준다.

```python
gray = np.dot(input_image[..., :3], [0.299, 0.587, 0.114])   # RGB 가중 평균
gray_image = np.stack([gray, gray, gray], axis=-1).astype(np.uint8)
```
- `[..., :3]` — 앞 차원은 그대로, 채널은 RGB 3개만 (알파 제외)
- 이미지로 출력하려면 다시 3채널로 쌓고 `uint8`로 캐스팅해야 한다.

### ex05 — 배달 메뉴 가격 계산기
딕셔너리를 그대로 UI 선택지로 재활용하는 패턴.

```python
gr.Dropdown(list(menu_prices.keys()), label="메뉴 선택")
gr.Slider(minimum=1, maximum=10, step=1, label="수량")
```

### ex06 — 에코 챗봇 / LLM 연동
`gr.ChatInterface(fn)`의 함수는 반드시 `(message, history)` 두 개를 받는다.

- `message` : 방금 입력한 말
- `history` : 이전 대화 기록. `[{"role": "user", ...}, {"role": "assistant", ...}]` 형태
- 한 턴이 2개 항목이라 **대화 횟수 = `len(history) // 2 + 1`**

같은 노트북에 OpenAI(`gpt-4o-mini`) 연동, HuggingFace `transformers.pipeline` 로컬 모델 버전도 시도.

> ⚠️ OpenAI 셀에는 버그가 남아 있다. `message = [...]`로 매개변수를 덮어쓴 뒤
> `message.append({"content": message})`를 해서 자기 자신을 넣는다.
> 리스트 변수는 `messages` 같은 다른 이름으로 분리할 것.

### exex — Gemini 챗봇
`.env`의 `GEMINI_API_KEY` → `genai.Client(api_key=...)`.
Gradio history를 Gemini 형식으로 **변환**하는 것이 핵심.

| Gradio | Gemini |
|---|---|
| `role: "assistant"` | `role: "model"` |
| `content: "..."` | `parts: [{"text": "..."}]` |

키가 없으면 `raise ValueError(...)`로 먼저 끊어주는 방어 코드도 함께.

### ex07 — 카테고리별 요약 조회기
중첩 딕셔너리에서 값을 꺼내 **여러 출력에 순서대로 매핑**.

```python
return info["평균가격"], info["평균평점"], info["인기메뉴"]   # outputs 3개와 순서 일치
```
"실제로는 DB 쿼리 결과일 수도 있다" → ex10의 예고편.

### ex08 — Blocks로 만든 BMI 계산기
`gr.Interface`의 자동 배치를 벗어나 레이아웃을 직접 짠 첫 예제.

- `with gr.Blocks() as demo:` 안에서 컴포넌트를 **변수로 받아 둔다**
- `with gr.Row():` — 가로 배치
- `btn.click(fn=, inputs=[...], outputs=[...])` — 클릭 시점에만 실행
- BMI 구간: 18.5 미만 저체중 / 23 미만 정상 / 25 미만 과체중 / 이상 비만

### ex09 — CSV 업로드 분석 대시보드
**표 + 그래프를 한 화면에** 내보내는 패턴. Chapter01의 csv 파일로 테스트.

```python
df = pd.read_csv(file, encoding="utf-8-sig")     # file은 임시 "경로 문자열"
numeric_df = df.select_dtypes(include="number")  # 숫자형 컬럼만
summary_table = numeric_df.describe().round(2)

fig, ax = plt.subplots(figsize=(6, 4))
ax.hist(numeric_df[first_col], bins=10, color="skyblue", edgecolor="black")
return summary_table, fig                        # → gr.Dataframe, gr.Plot
```
- Gradio 6에서 `gr.File`은 기본 `type="filepath"` → 콜백에 **문자열 경로**가 들어온다 (`file.name` 아님)
- `plt.show()`가 아니라 **`fig` 객체를 return**해야 `gr.Plot`에 그려진다
- 숫자형 컬럼이 없는 경우까지 `ax.text(...)`로 대비

### ex10 — Oracle DB 실시간 조회 대시보드 ★
Chapter02(Oracle) + Chapter03(Gradio)을 합친 종합 실습이자 **ex11 과제의 롤모델**.

```python
query = "SELECT * FROM DELIVERY_ORDERS WHERE CATEGORY = :category"
with oracledb.connect(user=USER, password=PASSWORD, dsn=DSN) as conn:
    df = pd.read_sql(query, conn, params={"category": category})
```
- **바인드 변수 `:category`** — 입력값을 SQL 문자열에 직접 붙이지 않는다 (SQL Injection 방지)
- `with` 블록으로 커넥션 자동 반납
- 조회 결과 0건일 때 빈 DataFrame + "데이터 없음" 그래프를 돌려주는 **방어 코드**
- Blocks 구성: Dropdown + 조회 버튼 (Row) → 요약통계 표 + 가격 히스토그램 (Row)

### ex11 — 과제 브리핑 (진행 중)
농산물(KAMIS) 일별 가격을 **크롤링**해 이동평균·등락률을 보여주는 대시보드.
제출일 2026-09-03. 자세한 계획·데이터 소스·함정은 [`ex11_과제_브리핑.md`](./ex11_과제_브리핑.md) 참고.

### Titanic.ipynb (진행 중)
Gradio와 별개로 시작한 캐글 실습. 현재 문제 정의 → 데이터 수집 → EDA(결측치 확인, 범주형 막대차트)
→ Feature engineering 초입까지. `../data/train.csv`(891행), `../data/test.csv`(418행) 사용.

---

## 4. 자주 걸린 지점

1. **`demo.close()`를 빼먹으면** 포트가 계속 쌓인다. 셀 재실행 전에 닫기.
2. **`outputs` 개수 ≠ return 개수**면 에러. 순서까지 맞춰야 한다.
3. **그래프는 `fig`를 return** — `plt.show()`는 Gradio 화면에 아무것도 안 그린다.
4. **한글 깨짐** — `mpl.rc('font', family='AppleGothic')`을 그래프 그리기 전에 실행.
5. **`gr.File`은 경로 문자열** (Gradio 6 기준). `file.name`으로 접근하면 안 된다.
6. **`ChatInterface`의 함수 시그니처는 `(message, history)` 고정.**
7. **DB 조회는 바인드 변수로.** 문자열 포매팅으로 SQL을 만들지 않는다.

---

## 5. 다음 단계

- ex11 과제 — 크롤링(Chapter01) → 정제/통계(Chapter02) → Gradio 대시보드(Chapter03) 전체 연결
- 보너스: 크롤링 결과를 Oracle에 적재한 뒤 ex10 구조로 조회
