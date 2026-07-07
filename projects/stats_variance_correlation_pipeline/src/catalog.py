from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path


DEFAULT_SOURCE_ROOT = Path("D:/\u9879\u76ee\u6587\u4ef6202605/\u5236\u56fe\u6570\u636e")


@dataclass(frozen=True)
class ResultAsset:
    asset_id: str
    title: str
    source_relative_path: str
    packaged_name: str
    asset_type: str
    role: str
    notes: str

    def source_path(self, source_root: Path) -> Path:
        return source_root / self.source_relative_path

    def as_json(self, source_root: Path) -> dict[str, str]:
        row = asdict(self)
        row["original_source_path"] = str(self.source_path(source_root))
        return row


@dataclass(frozen=True)
class SourceDataset:
    dataset_id: str
    title: str
    source_relative_path: str
    packaged_relative_path: str
    table_shape: str
    notes: str

    def source_path(self, source_root: Path) -> Path:
        return source_root / self.source_relative_path

    def as_json(self, source_root: Path) -> dict[str, str]:
        row = asdict(self)
        row["original_source_path"] = str(self.source_path(source_root))
        return row


SELECTED_RESULT_ASSETS: tuple[ResultAsset, ...] = (
    ResultAsset(
        asset_id="nh4n_research_pdf",
        title="NH4-N methodB2v2 scientific result",
        source_relative_path="\u79d1\u7814\u7528\u56fe_B2v2v3/Fig_NH4N_methodB2v2_01.pdf",
        packaged_name="Fig_NH4N_methodB2v2_01.pdf",
        asset_type="pdf",
        role="scientific_result_original",
        notes="Frozen publication-style PDF selected from the approved scientific figure directory.",
    ),
    ResultAsset(
        asset_id="no3n_research_pdf",
        title="NO3-N methodB2v2 scientific result",
        source_relative_path="\u79d1\u7814\u7528\u56fe_B2v2v3/Fig_NO3N_methodB2v2_01.pdf",
        packaged_name="Fig_NO3N_methodB2v2_01.pdf",
        asset_type="pdf",
        role="scientific_result_original",
        notes="Frozen publication-style PDF selected from the approved scientific figure directory.",
    ),
    ResultAsset(
        asset_id="no3n_spss_png",
        title="NO3-N SPSS source result image",
        source_relative_path="SPSS\u539f\u6570\u636e\u56fe\u7247/NO3-N.png",
        packaged_name="SPSS_NO3-N.png",
        asset_type="image",
        role="spss_result_original",
        notes="Original SPSS result image paired with the NO3-N scientific result.",
    ),
)


SELECTED_SOURCE_DATASETS: tuple[SourceDataset, ...] = (
    SourceDataset(
        dataset_id="soil_core_long_cn",
        title="Soil core variables long table with original Chinese factor labels",
        source_relative_path="data/clean/soil_core_variables_latest_long.csv",
        packaged_relative_path="data/clean/soil_core_variables_latest_long.csv",
        table_shape="long",
        notes="Exact copied clean source CSV; not modified or recalculated.",
    ),
    SourceDataset(
        dataset_id="soil_core_long_v3",
        title="Soil core variables long table with normalized factor labels",
        source_relative_path="data/clean/soil_core_variables_latest_v3_long.csv",
        packaged_relative_path="data/clean/soil_core_variables_latest_v3_long.csv",
        table_shape="long",
        notes="Exact copied clean source CSV; suitable for optional pipeline demonstrations.",
    ),
    SourceDataset(
        dataset_id="soil_physicochemical_wide_cn",
        title="Soil physicochemical wide table with original Chinese factor labels",
        source_relative_path="data/clean/soil_physicochemical_latest_wide.csv",
        packaged_relative_path="data/clean/soil_physicochemical_latest_wide.csv",
        table_shape="wide",
        notes="Exact copied clean source CSV containing NO3_N, NH4_N, N_availability, pH, and moisture fields.",
    ),
    SourceDataset(
        dataset_id="soil_physicochemical_wide_v3",
        title="Soil physicochemical wide table with normalized factor labels",
        source_relative_path="data/clean/soil_physicochemical_latest_v3_wide.csv",
        packaged_relative_path="data/clean/soil_physicochemical_latest_v3_wide.csv",
        table_shape="wide",
        notes="Exact copied clean source CSV; recommended optional analysis input.",
    ),
)


SOURCE_SCAN_SUMMARY = {
    "source_root": str(DEFAULT_SOURCE_ROOT),
    "first_party_effective_code_assets": 64,
    "excluded": "third-party r_libs examples, temp/test/copy paths, duplicate scripts, and fragmented templates",
    "theme_counts": {
        "variance_analysis": 57,
        "correlation_analysis": 0,
        "data_cleaning": 50,
        "statistical_plotting": 43,
        "pdf_report_generation": 41,
    },
    "data_boundary": "Clean source CSV files from data/clean are copied byte-for-byte into data/clean; Excel/SAV/manifest files are not modified.",
    "statistical_boundary": "Historical ANOVA, post-hoc tests, CLD letters, and frozen figures are not recomputed.",
}


REPRESENTATIVE_CODE_ASSETS = (
    "scripts/run_nematode_remaining9_oneway_tukey_20260529.R",
    "scripts/run_nematode_remaining9_threeway_anova_20260529.R",
    "scripts/build_soil_NO3_update_0529_fresh.R",
    "scripts/plot_soil_NO3_update_0529.R",
    "outputs/oneway_significance_redraw_20260529/scripts/generate_oneway_audit_figures.py",
    "outputs/figures_clean_v5_layout_refined/scripts/plot_clean_single_indicator_figures_v5_layout_refined.py",
    "outputs/soil_NO3_methodB2v2_20260531/scripts/restyle_soil_NO3_methodB2v2_20260531.py",
    "outputs/soil_6remaining_methodB2v2_20260531/scripts/plot_soil_6remaining_methodB2v2_20260531.py",
    "outputs/nematode_subset_methodB2v2_20260531/scripts/plot_nematode_subset_methodB2v2_20260531.py",
    "outputs/plant_growth_methodB2v2_20260531/scripts/restyle_plant_growth_methodB2v2_20260531.py",
    "outputs/PPI_methodB2v2_20260531/scripts/plot_PPI_methodB2v2_20260531.py",
)
