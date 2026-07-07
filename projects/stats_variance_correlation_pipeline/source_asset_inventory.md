# Source Asset Inventory

## Provenance

- Scanned root: `D:\项目文件202605\制图数据`
- Approved scientific figure directory: `D:\项目文件202605\制图数据\科研用图_B2v2v3`
- SPSS image directory: `D:\项目文件202605\制图数据\SPSS原数据图片`
- Source CSV copied into this module: none
- Source Excel/SAV/manifest files modified: none

## Filtering Rules

The scan retained project-owned scripts under `scripts/` and `outputs/` and removed:

- third-party examples under `r_libs/`;
- temporary, test, backup, copy, and template-fragment paths;
- exact duplicate scripts by content hash;
- data files that were only inventoried and not needed as portfolio artifacts.

## Effective Code Asset Counts

- First-party effective code assets retained: 64
- variance_analysis: 57
- correlation_analysis: 0
- data_cleaning: 50
- statistical_plotting: 43
- pdf_report_generation: 41

The scan did not identify a clear first-party historical correlation-matrix script after filtering. Correlation logic is therefore provided as a reusable method for future input data, not claimed as a frozen historical output.

## Selected Result Assets

- scientific PDF original: `D:\项目文件202605\制图数据\科研用图_B2v2v3\Fig_NH4N_methodB2v2_01.pdf` -> `outputs/result_assets/original/Fig_NH4N_methodB2v2_01.pdf`
- scientific PDF original: `D:\项目文件202605\制图数据\科研用图_B2v2v3\Fig_NO3N_methodB2v2_01.pdf` -> `outputs/result_assets/original/Fig_NO3N_methodB2v2_01.pdf`
- SPSS result image: `D:\项目文件202605\制图数据\SPSS原数据图片\NO3-N.png` -> `outputs/result_assets/original/SPSS_NO3-N.png`

## Scientific PDF Candidates

- `科研用图_B2v2v3\Fig_Ba_abundance_methodB2v2_01.pdf` (46329 bytes)
- `科研用图_B2v2v3\Fig_BI_methodB2v2_01.pdf` (44249 bytes)
- `科研用图_B2v2v3\Fig_CI_methodB2v2_01.pdf` (43666 bytes)
- `科研用图_B2v2v3\Fig_EI_methodB2v2_01.pdf` (42827 bytes)
- `科研用图_B2v2v3\Fig_Fu_abundance_methodB2v2_01.pdf` (46829 bytes)
- `科研用图_B2v2v3\Fig_Fu_proportion_methodB2v2_01.pdf` (47208 bytes)
- `科研用图_B2v2v3\Fig_H_prime_methodB2v2_01.pdf` (43485 bytes)
- `科研用图_B2v2v3\Fig_J_methodB2v2_01.pdf` (42451 bytes)
- `科研用图_B2v2v3\Fig_Leaf_length_methodB2v2_01.pdf` (20520 bytes)
- `科研用图_B2v2v3\Fig_Leaf_number_methodB2v2_01.pdf` (15779 bytes)
- `科研用图_B2v2v3\Fig_Leaf_width_methodB2v2_01.pdf` (20927 bytes)
- `科研用图_B2v2v3\Fig_MI_methodB2v2_01.pdf` (42717 bytes)
- `科研用图_B2v2v3\Fig_N_availability_methodB2v2_01.pdf` (21310 bytes)
- `科研用图_B2v2v3\Fig_NH4N_methodB2v2_01.pdf` (17554 bytes)
- `科研用图_B2v2v3\Fig_NO3N_methodB2v2_01.pdf` (18172 bytes)
- `科研用图_B2v2v3\Fig_Om_OP_abundance_methodB2v2_01.pdf` (50511 bytes)
- `科研用图_B2v2v3\Fig_Om_OP_proportion_methodB2v2_01.pdf` (49800 bytes)
- `科研用图_B2v2v3\Fig_pH_methodB2v2_01.pdf` (17457 bytes)
- `科研用图_B2v2v3\Fig_Plant_height_methodB2v2_01.pdf` (20363 bytes)
- `科研用图_B2v2v3\Fig_Pp_abundance_methodB2v2_01.pdf` (48134 bytes)
- `科研用图_B2v2v3\Fig_Pp_proportion_methodB2v2_01.pdf` (46913 bytes)
- `科研用图_B2v2v3\Fig_PPI_methodB2v2_01.pdf` (44845 bytes)
- `科研用图_B2v2v3\Fig_Root_biomass_methodB2v2_01.pdf` (16315 bytes)
- `科研用图_B2v2v3\Fig_S_methodB2v2_01.pdf` (42999 bytes)
- `科研用图_B2v2v3\Fig_Shoot_biomass_methodB2v2_01.pdf` (16666 bytes)
- `科研用图_B2v2v3\Fig_SI_methodB2v2_01.pdf` (44556 bytes)
- `科研用图_B2v2v3\Fig_Simpson_lambda_methodB2v2_01.pdf` (48902 bytes)
- `科研用图_B2v2v3\Fig_SOC_methodB2v2_01.pdf` (17664 bytes)
- `科研用图_B2v2v3\Fig_Soil_moisture_methodB2v2_01.pdf` (17697 bytes)
- `科研用图_B2v2v3\Fig_SR_methodB2v2_01.pdf` (44845 bytes)
- `科研用图_B2v2v3\Fig_Stem_diameter_methodB2v2_01.pdf` (20304 bytes)
- `科研用图_B2v2v3\Fig_TC_methodB2v2_01.pdf` (17502 bytes)
- `科研用图_B2v2v3\Fig_TN_methodB2v2_01.pdf` (17148 bytes)
- `科研用图_B2v2v3\Fig_Total_abundance_methodB2v2_01.pdf` (48438 bytes)

## Effective Historical Code Assets

- `outputs/AUDIT_PPI_calc_chain_20260531/run_ppi_calc_chain_audit.py` | themes: variance_analysis, data_cleaning, pdf_report_generation
- `outputs/figures_clean_v4/scripts/plot_clean_single_indicator_figures_v4.py` | themes: variance_analysis, data_cleaning, statistical_plotting, pdf_report_generation
- `outputs/figures_clean_v5_layout_refined/scripts/plot_clean_single_indicator_figures_v5_layout_refined.py` | themes: variance_analysis, data_cleaning, statistical_plotting, pdf_report_generation
- `outputs/figures_clean_v5_layout_refined/scripts/plot_N_availability_split_panels_v5.py` | themes: variance_analysis, data_cleaning, statistical_plotting, pdf_report_generation
- `outputs/figures_clean_v5_light/scripts/plot_clean_single_indicator_figures_v5_light.py` | themes: variance_analysis, data_cleaning, statistical_plotting, pdf_report_generation
- `outputs/figures_clean_v6_targeted/scripts/plot_v6_targeted_fixes.py` | themes: variance_analysis, data_cleaning, statistical_plotting, pdf_report_generation
- `outputs/figures_for_review/scripts/plot_Fig1_soil_TN_TC_SOC_review_v1.py` | themes: variance_analysis, data_cleaning, statistical_plotting
- `outputs/figures_for_review/scripts/plot_FigS1_soil_pH_moisture_noCLD_review_v1.py` | themes: variance_analysis, data_cleaning, statistical_plotting
- `outputs/nematode_remaining9_methodB2v2_20260531/scripts/plot_nematode_remaining9_methodB2v2_20260531.py` | themes: variance_analysis, data_cleaning, statistical_plotting
- `outputs/nematode_remaining9_plotting_20260529_batch_v1/scripts/plot_nematode_remaining9_batch_v1_20260529.R` | themes: variance_analysis, data_cleaning, pdf_report_generation
- `outputs/nematode_subset_methodB2v2_20260531/scripts/plot_nematode_subset_methodB2v2_20260531.py` | themes: variance_analysis, data_cleaning, statistical_plotting
- `outputs/nematode_subset_plotting_20260529_batch_v1/scripts/plot_nematode_subset_batch_v1_20260529.py` | themes: variance_analysis, data_cleaning, statistical_plotting
- `outputs/nematode_subset_plotting_20260529_batch_v1_1/scripts/plot_nematode_subset_batch_v1_1_20260529.py` | themes: variance_analysis, data_cleaning, statistical_plotting
- `outputs/oneway_significance_redraw_20260529/scripts/fix_cld_letters_from_pairwise.py` | themes: variance_analysis, data_cleaning
- `outputs/oneway_significance_redraw_20260529/scripts/generate_oneway_audit_figures.py` | themes: variance_analysis, data_cleaning, statistical_plotting, pdf_report_generation
- `outputs/plant_growth_20260529_batch_v1/plot_plant_growth_batch_v1_20260530.R` | themes: variance_analysis, statistical_plotting, pdf_report_generation
- `outputs/plant_growth_methodB2_20260531/scripts/restyle_plant_growth_methodB2_20260531.py` | themes: variance_analysis, data_cleaning, statistical_plotting, pdf_report_generation
- `outputs/plant_growth_methodB2v2_20260531/scripts/restyle_plant_growth_methodB2v2_20260531.py` | themes: variance_analysis, data_cleaning, statistical_plotting, pdf_report_generation
- `outputs/PPI_methodB2v2_20260531/scripts/plot_PPI_methodB2v2_20260531.py` | themes: variance_analysis, data_cleaning, statistical_plotting, pdf_report_generation
- `outputs/PPI_methodB_20260531/scripts/plot_PPI_methodB_20260531.py` | themes: variance_analysis, data_cleaning, statistical_plotting, pdf_report_generation
- `outputs/PPI_methodB_20260531_patch01/scripts/freeze_replace_ppi_patch01_20260531.py` | themes: variance_analysis, data_cleaning, pdf_report_generation
- `outputs/PPI_methodB_20260531_patch01/scripts/plot_PPI_methodB_patch01_20260531.py` | themes: variance_analysis, data_cleaning, statistical_plotting, pdf_report_generation
- `outputs/PPI_recompute_corrected_20260531/recompute_ppi_corrected_20260531.py` | themes: variance_analysis, data_cleaning
- `outputs/PPI_recompute_corrected_20260531/run_ppi_corrected_oneway_tukey_20260531.R` | themes: variance_analysis
- `outputs/restyle_20260530/figures_nematode_remaining9_absolute_methodB_01/scripts/restyle_nematode_remaining9_absolute_methodB_20260530.py` | themes: variance_analysis, data_cleaning, statistical_plotting, pdf_report_generation
- `outputs/restyle_20260530/figures_nematode_subset_methodB_01/scripts/restyle_nematode_subset_methodB_20260530.py` | themes: variance_analysis, data_cleaning, statistical_plotting, pdf_report_generation
- `outputs/restyle_20260530/figures_nematode_subset_methodB_02_safe3/scripts/restyle_nematode_subset_methodB_02_safe3_20260530.py` | themes: variance_analysis, data_cleaning, statistical_plotting, pdf_report_generation
- `outputs/restyle_20260530/figures_nematode_subset_methodB_03_Hprime/scripts/restyle_nematode_subset_methodB_03_Hprime_20260531.py` | themes: variance_analysis, data_cleaning, statistical_plotting, pdf_report_generation
- `outputs/restyle_20260530/figures_plant_growth_methodB_patch01/scripts/restyle_plant_growth_methodB_patch01_20260530.py` | themes: variance_analysis, data_cleaning, statistical_plotting, pdf_report_generation
- `outputs/restyle_20260530/figures_remaining_safe_methodB_newwindow_01/scripts/restyle_remaining_safe_nematode_methodB_newwindow_20260530.py` | themes: variance_analysis, data_cleaning, statistical_plotting, pdf_report_generation
- `outputs/restyle_20260530/figures_remaining_safe_methodB_newwindow_01/scripts/restyle_remaining_safe_plant_growth_methodB_newwindow_20260530.R` | themes: variance_analysis, statistical_plotting, pdf_report_generation
- `outputs/restyle_20260530/plot_style.py` | themes: data_cleaning, statistical_plotting
- `outputs/restyle_20260530/plot_style.R` | themes: statistical_plotting
- `outputs/restyle_20260530/scripts/restyle_plant_growth_axisfix_01_20260530.R` | themes: variance_analysis, statistical_plotting, pdf_report_generation
- `outputs/restyle_20260530/scripts/restyle_plant_growth_complete_v3_20260530.R` | themes: variance_analysis, statistical_plotting, pdf_report_generation
- `outputs/restyle_20260530/scripts/restyle_plant_growth_smallbatch_01_20260530.R` | themes: variance_analysis, statistical_plotting, pdf_report_generation
- `outputs/restyle_20260530/scripts/restyle_plant_growth_smallbatch_02_20260530.R` | themes: variance_analysis, statistical_plotting, pdf_report_generation
- `outputs/restyle_20260530/scripts/restyle_root_biomass_markercheck_20260530.R` | themes: variance_analysis, statistical_plotting, pdf_report_generation
- `outputs/revised_single_factor_20260522/figures/plot_revised_v2_common.py` | themes: data_cleaning, statistical_plotting, pdf_report_generation
- `outputs/revised_single_factor_20260522/figures/plot_single_indicator_v3.py` | themes: data_cleaning, statistical_plotting, pdf_report_generation
- `outputs/soil_6remaining_methodB2v2_20260531/scripts/plot_soil_6remaining_methodB2v2_20260531.py` | themes: variance_analysis, data_cleaning, statistical_plotting, pdf_report_generation
- `outputs/soil_6remaining_methodB_20260531/scripts/patch_pH_ylower6_20260531.py` | themes: variance_analysis, data_cleaning, statistical_plotting, pdf_report_generation
- `outputs/soil_6remaining_methodB_20260531/scripts/plot_soil_6remaining_methodB_20260531.py` | themes: variance_analysis, data_cleaning, statistical_plotting, pdf_report_generation
- `outputs/soil_NO3_methodB2v2_20260531/scripts/preflight_soil_NO3_methodB2v2_20260531.py` | themes: pdf_report_generation
- `outputs/soil_NO3_methodB2v2_20260531/scripts/restyle_soil_NO3_methodB2v2_20260531.py` | themes: variance_analysis, data_cleaning, statistical_plotting, pdf_report_generation
- `outputs/soil_NO3_methodB_20260531/scripts/restyle_soil_NO3_methodB_20260531.py` | themes: variance_analysis, data_cleaning, statistical_plotting, pdf_report_generation
- `outputs/visual_refine_20260529/数据/batch_plot_soil_v1_1.py` | themes: variance_analysis, data_cleaning, statistical_plotting, pdf_report_generation
- `outputs/visual_refine_20260529/数据/redraw_figures_from_fixed_cld.py` | themes: variance_analysis, data_cleaning, statistical_plotting, pdf_report_generation
- `scripts/06_generate_figures_revised_single_factor.R` | themes: variance_analysis, data_cleaning, statistical_plotting, pdf_report_generation
- `scripts/audit_nematode_remaining9_oneway_20260529.py` | themes: variance_analysis, data_cleaning
- `scripts/audit_nematode_workbook_20260529.py` | themes: data_cleaning
- `scripts/audit_sheet2_remaining3_20260529.py` | themes: variance_analysis, data_cleaning
- `scripts/audit_sheet2_remaining3_v2_20260529.py` | themes: variance_analysis, data_cleaning
- `scripts/build_nematode_remaining9_audit_20260529.py` | themes: variance_analysis, data_cleaning
- `scripts/build_nematode_remaining9_threeway_compare_20260529.py` | themes: variance_analysis, data_cleaning
- `scripts/build_nematode_subset_tables_20260529.py` | themes: variance_analysis, data_cleaning
- `scripts/build_soil_NO3_update_0529_fresh.R` | themes: variance_analysis, data_cleaning, statistical_plotting, pdf_report_generation
- `scripts/make_nematode_batch_v1_1_contact_sheet_20260529.py` | themes: data_cleaning, pdf_report_generation
- `scripts/nematode_oneway_subset_audit_20260529.py` | themes: variance_analysis, data_cleaning
- `scripts/plot_soil_NO3_update_0529.R` | themes: variance_analysis, data_cleaning, pdf_report_generation
- `scripts/run_nematode_oneway_emmeans_subset_20260529.R` | themes: variance_analysis
- `scripts/run_nematode_remaining9_oneway_tukey_20260529.R` | themes: variance_analysis
- `scripts/run_nematode_remaining9_threeway_anova_20260529.R` | themes: variance_analysis
- `scripts/run_soil_NO3_update_pairwise_0529.R` | themes: variance_analysis

## Data Boundary

Historical CSV, Excel, SAV, and manifest files remain in the source corpus and were not copied, changed, or recalculated. The module packages frozen PDF/PNG result assets plus reusable code that can be run on explicitly supplied new data.

## Statistical Boundary

Historical ANOVA statistics, Tukey comparisons, CLD letters, and already frozen figures are treated as source outputs. They are not recomputed by the default pipeline.
