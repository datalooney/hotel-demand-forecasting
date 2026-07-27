### Deploying Forecast for 30 days
These are Streamlit UI components that improve the user experience.

---

# 1. `st.spinner()`

A spinner displays a loading animation while some code is running.

For example,

```python
with st.spinner("Generating forecasts..."):

    forecast_df = forecast_bookings(...)
```

When the user clicks **Generate Forecast**, the app immediately shows

```
⏳ Generating forecasts...
```

with a spinning indicator.

While the model is executing,

```
⏳ Generating forecasts...
```

is displayed.

Once `forecast_bookings()` finishes, the spinner automatically disappears.

Without it, the page would simply freeze for a few seconds, making the user wonder if anything is happening.

---

## It's equivalent to

```
Start
   │
   ▼
Show Loading Animation
   │
Run forecast_bookings()
   │
Forecast finished
   │
Hide Loading Animation
```

---

# 2. `st.success()`

This displays a green success message.

```python
st.success("Forecast Complete!")
```

produces something like

```
✅ Forecast Complete!
```

It's just a notification to tell the user that the operation completed successfully.

---

# Other message types

Streamlit provides several message styles:

### Success

```python
st.success("Forecast Complete!")
```

Output:

```
✅ Forecast Complete!
```

---

### Warning

```python
st.warning("Please select a date range.")
```

Output:

```
⚠ Please select a date range.
```

---

### Error

```python
st.error("Model file not found.")
```

Output:

```
❌ Model file not found.
```

---

### Information

```python
st.info("Forecasts are generated recursively.")
```

Output:

```
ℹ Forecasts are generated recursively.
```

---

# In your app

When the user clicks **Generate Forecast**, the flow is:

```
Click Button
      │
      ▼
⏳ Generating forecasts...

forecast_bookings()

      │
      ▼
Spinner disappears

      │
      ▼
✅ Forecast Complete!

      │
      ▼
Display table

      │
      ▼
Display plots
```

---

For your hotel forecasting dashboard, these are nice touches because forecasting may take a few seconds. Later, when you deploy the app, you can also add:

```python
st.balloons()
```

or

```python
st.toast("Forecast generated successfully!")
```

after a successful forecast. These aren't necessary, but they add a polished, interactive feel to the application.


`plotly.express (px)` and `plotly.graph_objects (go)` serve different purposes. They are built on the same underlying Plotly library, but at different levels of abstraction.

| Feature         | `plotly.express (px)`         | `plotly.graph_objects (go)` |
| --------------- | ----------------------------- | --------------------------- |
| Level           | High-level                    | Low-level                   |
| Code            | Very little                   | More verbose                |
| Multiple traces | Automatic                     | Manual                      |
| Customization   | Good                          | Excellent                   |
| Best for        | Exploratory plots, dashboards | Complex production plots    |

---

## 1. `px.line()`

You used

```python
fig = px.line(
    display_df,
    x="date",
    y="forecast",
    color="room_type",
    markers=True
)
```

Here you only specify

* dataframe
* x
* y
* color

and Plotly automatically

* groups data by `room_type`
* creates 3 traces
* assigns colors
* creates the legend
* orders the x-axis

You don't have to write any loop.

Internally it is almost equivalent to

```python
for room in display_df["room_type"].unique():
    go.Scatter(...)
```

---

## 2. `go.Scatter()`

This is much lower level.

For example

```python
fig = go.Figure()

fig.add_trace(
    go.Scatter(
        x=df["date"],
        y=df["forecast"],
        mode="lines+markers",
        name="Forecast"
    )
)
```

This creates **only one line**.

If you want another line

```python
fig.add_trace(
    go.Scatter(
        x=df["date"],
        y=df["actual_bookings"],
        mode="lines+markers",
        name="Actual"
    )
)
```

you must add it yourself.

If there are 3 room types

you need

```python
for room in rooms:
    fig.add_trace(...)
```

---

# Why I switched to go.Scatter

Suppose you want

Forecast

```
Deluxe Forecast
Standard Forecast
Suite Forecast
```

and also

Actual

```
Deluxe Actual
Standard Actual
Suite Actual
```

Now there are **6 independent lines**.

`px.line()` cannot directly say

> use column A for three lines and column B for another three lines.

It expects one y-column.

With `go.Scatter()` you can manually add

```
Forecast Deluxe
Forecast Standard
Forecast Suite
Actual Deluxe
Actual Standard
Actual Suite
```

exactly how you want.

That's why `go.Scatter` is usually chosen for comparison charts.

---

# Could we use `px.scatter()`?

Yes.

For example

```python
px.scatter(
    df,
    x="date",
    y="forecast",
    color="room_type"
)
```

produces only points.

If you want connected points

```python
px.line(..., markers=True)
```

is better.

---

# Why not `px.scatter()` here?

Forecasts are **time series**.

Time series are almost always represented with lines because the order of observations matters.

```
●────●────●────●
```

instead of

```
●   ●     ●     ●
```

---

# Can we make the comparison using only `plotly.express`?

Yes, but the dataframe has to be reshaped first.

Suppose your comparison dataframe is

| date  | room_type | forecast | actual |
| ----- | --------- | -------- | ------ |
| Dec 2 | Deluxe    | 35       | 37     |
| Dec 3 | Deluxe    | 36       | 39     |

You first convert it to

```python
plot_df = comparison_df.melt(
    id_vars=["date", "room_type"],
    value_vars=["forecast", "actual_bookings"],
    var_name="Type",
    value_name="Bookings"
)
```

which becomes

| date  | room_type | Type     | Bookings |
| ----- | --------- | -------- | -------- |
| Dec 2 | Deluxe    | forecast | 35       |
| Dec 2 | Deluxe    | actual   | 37       |
| Dec 3 | Deluxe    | forecast | 36       |
| Dec 3 | Deluxe    | actual   | 39       |

Now you can do

```python
fig = px.line(
    plot_df,
    x="date",
    y="Bookings",
    color="room_type",
    line_dash="Type",
    markers=True
)
```

This automatically creates:

* Deluxe Forecast (solid)
* Deluxe Actual (dashed)
* Standard Forecast
* Standard Actual
* Suite Forecast
* Suite Actual

with much less code.

### For your Streamlit app, I'd recommend this `melt()` + `px.line()` approach. It's cleaner, easier to maintain, and scales well if you later add another series (for example, predictions from each individual model in addition to the median forecast).
