import pandas as pd
import pytest
from app.services.analysis_engine import AnalysisEngine
from app.services.chart_engine import ChartEngine
from app.services.data_profiler import DataProfiler
from app.services.insight_engine import InsightEngine


@pytest.fixture
def test_df(sample_sales_data):
    return pd.DataFrame(sample_sales_data)


def test_profiler_identifies_column_types(test_df):
    profiler = DataProfiler()
    profile = profiler.profile(test_df)
    cols = profile["columns"]

    assert cols["Date"]["is_date"] is True
    assert cols["Product"]["is_categorical"] is True
    assert cols["Amount"]["is_numeric"] is True
    assert cols["Quantity"]["is_numeric"] is True


def test_profiler_detects_missing_values():
    df = pd.DataFrame({
        "ID": [1, 2, 3, 4, 5],
        "Score": [10.0, None, 30.0, None, 50.0],  # 2 out of 5 missing = 40%
    })
    profiler = DataProfiler()
    profile = profiler.profile(df)

    score_prof = profile["columns"]["Score"]
    assert score_prof["missing_count"] == 2
    assert score_prof["missing_pct"] == 40.0


def test_profiler_detects_duplicate_rows():
    df = pd.DataFrame({
        "A": [1, 2, 1, 3],
        "B": ["x", "y", "x", "z"],
    })
    profiler = DataProfiler()
    profile = profiler.profile(df)
    assert profile["duplicate_rows"] == 1


def test_profiler_infers_sales_dataset_type(test_df):
    profiler = DataProfiler()
    profile = profiler.profile(test_df)
    assert profile["dataset_type"]["type"] == "sales"
    assert profile["dataset_type"]["confidence"] >= 0.6


def test_analysis_engine_kpis(test_df):
    profiler = DataProfiler()
    profile = profiler.profile(test_df)

    engine = AnalysisEngine()
    analysis = engine.analyze(test_df, profile, dataset_type="sales")
    kpis = analysis["kpis"]

    titles = [k["title"] for k in kpis]
    assert any("Total Records" in t for t in titles)
    assert any("Total Amount" in t for t in titles)

    amount_kpi = next(k for k in kpis if "Total Amount" in k["title"])
    # 1200 + 50 + 300 + 2400 + 100 + 1200 = 5250
    assert float(amount_kpi["value"]) == 5250.0


def test_analysis_engine_totals_and_averages(test_df):
    profiler = DataProfiler()
    profile = profiler.profile(test_df)

    engine = AnalysisEngine()
    analysis = engine.analyze(test_df, profile, dataset_type="sales")
    kpis = analysis["kpis"]

    avg_kpi = next(k for k in kpis if "Avg Amount" in k["title"])
    # 5250 / 6 = 875.0
    assert float(avg_kpi["value"]) == 875.0


def test_insight_engine_high_missing_values():
    df = pd.DataFrame({
        "A": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
        "SparseCol": [None, None, 1.0, None, None, None, 2.0, None, None, None],  # 80% missing
    })
    profiler = DataProfiler()
    profile = profiler.profile(df)

    insight_engine = InsightEngine()
    insights = insight_engine.generate_insights(df, profile, {}, dataset_type="general")

    dq_insights = [i for i in insights if i["category"] == "data_quality" and "SparseCol" in i["title"]]
    assert len(dq_insights) > 0
    assert "80.0%" in dq_insights[0]["metric_value"]


def test_chart_engine_returns_valid_line_spec(test_df):
    profiler = DataProfiler()
    profile = profiler.profile(test_df)

    analysis_engine = AnalysisEngine()
    analysis = analysis_engine.analyze(test_df, profile, dataset_type="sales")

    chart_engine = ChartEngine()
    charts = chart_engine.generate_charts(test_df, profile, analysis, dataset_type="sales")

    line_charts = [c for c in charts if c["type"] == "line"]
    assert len(line_charts) > 0
    spec = line_charts[0]
    assert "data" in spec
    assert len(spec["data"]) > 0
    assert "name" in spec["data"][0]
    assert "value" in spec["data"][0]
