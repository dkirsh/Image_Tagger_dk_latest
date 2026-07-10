"""Central catalogue: which adapters exist, which `cnfa.*` key each function
fills, and the licence gate that decides what a given build may enable.

This is the machine-readable form of the "which function fills which stub"
cheat-sheet. Two tests lean on it (tests/test_registry.py): every key an
adapter `provides` must appear in STUB_TO_FUNCTION, and no two *enabled*
permissive adapters may silently own the same key.
"""
from __future__ import annotations

from typing import Dict, Iterable, List

from .base import AnalyzerAdapter, License
from .permissive.aesthetics_toolbox_adapter import AestheticsToolboxAdapter
from .permissive.colour_adapter import ColourAdapter
from .permissive.colour_opponent_adapter import ColourOpponentAdapter
from .permissive.mahotas_texture_adapter import MahotasTextureAdapter
from .permissive.operators_v2_adapter import OperatorsV2Adapter
from .permissive.proximal_stats_adapter import ProximalStatsAdapter
from .permissive.skimage_texture_adapter import SkimageTextureAdapter
from .permissive.visual_clutter_adapter import VisualClutterAdapter
from .spatial.acoustic_adapter import AcousticPrivacyAdapter
from .spatial.reflection_adapter import ReflectionExposureAdapter
from .spatial.isovist_adapter import IsovistAdapter
from .spatial.prospect_refuge import ProspectRefugeAdapter
from .workers.aesthetic_score_adapter import AestheticScoreAdapter
from .workers.depth_midas_adapter import DepthMidasAdapter
from .workers.material_from_image_adapter import MaterialFromImageAdapter
from .workers.memorability_adapter import MemorabilityAdapter
from .workers.saliency_deepgaze_adapter import SaliencyDeepGazeAdapter
from .workers.segmentation_sam_adapter import SegmentationSamAdapter

PERMISSIVE_ADAPTERS: List[type[AnalyzerAdapter]] = [
    AestheticsToolboxAdapter,
    VisualClutterAdapter,
    ColourAdapter,
    SkimageTextureAdapter,
    ProximalStatsAdapter,
    ColourOpponentAdapter,
    MahotasTextureAdapter,
    OperatorsV2Adapter,   # Codex flagship five (canonical names)
    IsovistAdapter,     # plan-side; no-ops on image-only frames
    ProspectRefugeAdapter,   # plan-side; prospect/refuge/privacy/dead-ground
    AcousticPrivacyAdapter,  # plan-side; calibrated speech-privacy (needs pyroomacoustics)
    ReflectionExposureAdapter,  # plan-side; specular self-exposure + seen-via-reflection
]

WORKER_ADAPTERS: List[type[AnalyzerAdapter]] = [
    DepthMidasAdapter,
    SegmentationSamAdapter,
    SaliencyDeepGazeAdapter,
    MemorabilityAdapter,
    AestheticScoreAdapter,
    MaterialFromImageAdapter,
]

ALL_ADAPTERS: List[type[AnalyzerAdapter]] = PERMISSIVE_ADAPTERS + WORKER_ADAPTERS

# --- the cheat-sheet, as data: cnfa key -> callable that fills it ------------
STUB_TO_FUNCTION: Dict[str, str] = {
    # Aesthetics-Toolbox (MIT)
    "cnfa.fractal_dimension": "AT.fractal_dimension_qips.fractal_dimension_2d",
    "cnfa.fluency.spectral_slope": "AT.fourier_qips.fourier_slope_branka_Spehar_Isherwood",
    "cnfa.fluency.visual_entropy_spatial": "AT.edge_entropy_qips.do_first_and_second_order_entropy_and_edge_density[0]",
    "cnfa.fluency.second_order_entropy": "AT.edge_entropy_qips.do_first_and_second_order_entropy_and_edge_density[1]",
    "cnfa.fluency.edge_clarity_mean": "AT.edge_entropy_qips.do_first_and_second_order_entropy_and_edge_density[2]",
    "cnfa.fluency.symmetry_score_horizontal": "AT.balance_qips.Mirror_symmetry",
    "cnfa.fluency.balance_qip": "AT.balance_qips.Balance",
    "cnfa.fluency.pattern_rhythm_regularity": "AT.balance_qips.Homogeneity",
    "cnfa.fluency.self_similarity": "AT.PHOG_qips.PHOGfromImage[0]",
    "cnfa.fluency.hierarchy_depth": "AT.PHOG_qips.PHOGfromImage[1]",
    "cnfa.fluency.anisotropy": "AT.PHOG_qips.PHOGfromImage[2]",
    "cnfa.fluency.color_palette_entropy": "AT.color_and_simple_qips.shannonentropy_channels",
    # visual-clutter (MIT/BSD)
    "cnfa.fluency.clutter_density_count": "visual_clutter.Vlc.getClutter_FC",
    "cnfa.fluency.subband_entropy_clutter": "visual_clutter.Vlc.getClutter_SE",
    # colour-science (BSD)
    "cnfa.light.cct_kelvin": "colour.temperature.xy_to_CCT",
    "cnfa.light.warm_vs_cool_ratio": "colour.temperature.xy_to_CCT(normalised)",
    "cnfa.fluency.colorfulness": "hasler_susstrunk_colourfulness",
    # scikit-image (BSD)
    "cnfa.haptic.texture_variation_index": "skimage.feature.graycoprops(contrast)",
    "cnfa.haptic.glcm_homogeneity": "skimage.feature.graycoprops(homogeneity)",
    "cnfa.haptic.glcm_energy": "skimage.feature.graycoprops(energy)",
    "cnfa.haptic.glcm_correlation": "skimage.feature.graycoprops(correlation)",
    "cnfa.geometry.curvilinearity": "skimage.feature.shape_index",
    # operators_v2 — Codex flagship five (canonical names; native/permissive)
    "cnfa.contour.curvilinear_ratio": "operators_v2._curvilinear_ratio (contour curvature)",
    "cnfa.salience.attention_concentration": "operators_v2 spectral-residual saliency",
    "cnfa.biophilic.green_view_ratio": "operators_v2 ExG vegetation index",
    "cnfa.spatial.depth_openness_index": "operators_v2 (frame.depth_map)",
    # (5th flagship, cnfa.fluency.pattern_rhythm_regularity, is owned by aesthetics_toolbox)
    # proximal-stats (native; permissive)
    "cnfa.light.luminance_mean": "native.luminance_mean",
    "cnfa.light.rms_contrast": "native.rms_contrast",
    "cnfa.material.luminance_skew": "scipy.stats.skew(luminance)  [Motoyoshi gloss cue]",
    "cnfa.material.luminance_kurtosis": "scipy.stats.kurtosis(luminance)",
    "cnfa.material.subband_skew": "scipy.stats.skew(highpass luminance)",
    "cnfa.geometry.edge_density_canny": "cv2.Canny density",
    "cnfa.geometry.straight_edge_ratio": "cv2.HoughLinesP / edge pixels",
    "cnfa.dynamic.depth_of_field": "skimage.measure.blur_effect",
    "cnfa.fluency.radial_spectral_slope": "native radial FFT power-law fit",
    "cnfa.fluency.symmetry_lr_corr": "native left-right mirror correlation",
    "cnfa.fluency.symmetry_tb_corr": "native top-bottom mirror correlation",
    # colour-opponent (skimage + colour-science; BSD)
    "cnfa.color.lab_lightness_mean": "skimage.color.rgb2lab L*",
    "cnfa.color.lab_lightness_std": "skimage.color.rgb2lab L* SD",
    "cnfa.color.opponent_rg_mean": "rgb2lab a* mean (red-green)",
    "cnfa.color.opponent_by_mean": "rgb2lab b* mean (blue-yellow)",
    "cnfa.color.opponent_rg_energy": "mean|a*|",
    "cnfa.color.opponent_by_energy": "mean|b*|",
    "cnfa.color.hue_entropy": "HSV hue-histogram entropy (saturation-weighted)",
    "cnfa.color.saturation_mean": "HSV saturation mean",
    "cnfa.color.saturation_std": "HSV saturation SD",
    "cnfa.color.dominant_wavelength_nm": "colour.dominant_wavelength",
    # mahotas texture/shape (MIT)
    "cnfa.haptic.haralick_contrast": "mahotas.features.haralick[1]",
    "cnfa.haptic.haralick_correlation": "mahotas.features.haralick[2]",
    "cnfa.haptic.haralick_entropy": "mahotas.features.haralick[8]",
    "cnfa.haptic.haralick_energy": "mahotas.features.haralick[0]",
    "cnfa.haptic.lbp_entropy": "mahotas.features.lbp -> entropy",
    "cnfa.geometry.zernike_magnitude": "mahotas.features.zernike_moments -> norm",
    # isovist engine (clean-room; owned build)
    "cnfa.spatial.isovist_area": "spatial.isovist.isovist_measures->area",
    "cnfa.spatial.isovist_perimeter": "spatial.isovist.isovist_measures->perimeter",
    "cnfa.spatial.isovist_occlusivity": "spatial.isovist.isovist_measures->occlusivity",
    "cnfa.spatial.isovist_compactness": "spatial.isovist.isovist_measures->compactness",
    "cnfa.spatial.isovist_min_radial": "spatial.isovist.isovist_measures->min_radial",
    "cnfa.spatial.isovist_max_radial": "spatial.isovist.isovist_measures->max_radial",
    "cnfa.spatial.isovist_mean_radial": "spatial.isovist.isovist_measures->mean_radial",
    "cnfa.spatial.isovist_variance": "spatial.isovist.isovist_measures->radial_variance",
    "cnfa.spatial.isovist_skewness": "spatial.isovist.isovist_measures->radial_skewness",
    "cnfa.spatial.isovist_drift": "spatial.isovist.isovist_measures->drift_magnitude",
    "cnfa.spatial.isovist_elongation": "spatial.isovist.isovist_measures->elongation",
    "cnfa.spatial.isovist_jaggedness": "spatial.isovist.isovist_measures->jaggedness",
    "cnfa.spatial.isovist_dispersion": "spatial.isovist.isovist_measures->dispersion",
    "cnfa.topology.connectivity": "spatial.isovist.visibility_graph->connectivity",
    "cnfa.topology.mean_depth": "spatial.isovist.visibility_graph->mean_depth",
    "cnfa.topology.integration_value": "spatial.isovist.visibility_graph->integration",
    "cnfa.topology.clustering_coefficient": "spatial.isovist.visibility_graph->clustering",
    "cnfa.topology.intelligibility": "spatial.isovist.visibility_graph->intelligibility",
    "cnfa.topology.mean_integration": "spatial.isovist.visibility_graph->mean_integration",
    # prospect / refuge / privacy / dead-ground / first-detection (clean-room)
    "cnfa.spatial.prospect_depth": "spatial.prospect_refuge (max sightline / warning depth)",
    "cnfa.spatial.refuge_enclosure": "spatial.prospect_refuge (solid-boundary fraction)",
    "cnfa.spatial.dead_ground_ratio": "spatial.prospect_refuge.dead_ground_ratio",
    "cnfa.spatial.first_detection_distance": "spatial.prospect_refuge.first_detection_distance (min-exposure path)",
    "cnfa.spatial.visual_exposure": "spatial.prospect_refuge.visual_exposure",
    "cnfa.spatial.privacy_index": "spatial.prospect_refuge (1 - exposure)",
    "cnfa.spatial.prospect_refuge_index": "spatial.prospect_refuge (depth x enclosure x (1-dead_ground))",
    "cnfa.social.covisibility_potential": "spatial.prospect_refuge.social_covisibility",
    # calibrated acoustics — pyroomacoustics RIR + ISO-3382 STI (MIT)
    "cnfa.acoustic.rt60": "spatial.acoustic_pyroom.calibrated_fields->rt60",
    "cnfa.acoustic.speech_privacy": "spatial.acoustic_pyroom (1 - overheard STI fraction)",
    "cnfa.acoustic.overheard_fraction": "spatial.acoustic_pyroom (STI>threshold floor fraction)",
    "cnfa.acoustic.sti_mean": "spatial.acoustic_pyroom.calibrated_fields->mean STI",
    # specular self-exposure — mirror-image optics (clean-room)
    "cnfa.reflection.self_exposure": "spatial.reflection_exposure.self_exposure (raw reflectance*subtended)",
    "cnfa.reflection.self_exposure_index": "spatial.reflection_exposure.self_exposure (squashed 0..1)",
    "cnfa.reflection.self_image_count": "spatial.reflection_exposure.self_images (count)",
    "cnfa.reflection.nearest_self_image_distance": "spatial.reflection_exposure (min round-trip 2d)",
    "cnfa.reflection.reflected_exposure": "spatial.reflection_exposure.seen_via_reflection (bounced-sightline fraction)",
    # depth worker — MiDaS (MIT)
    "cnfa.spatial.enclosure_index": "midas_worker->reduce",
    "cnfa.spatial.isovist_openness": "midas_worker->reduce",
    "cnfa.spatial.ceiling_height_avg": "midas_worker->reduce",
    "cnfa.spatial.prospect_to_refuge_ratio": "midas_worker->reduce",
    "cnfa.dynamic.texture_gradient": "midas_worker->reduce",
    # segmentation worker — SAM/OneFormer (Apache; gate NC weights)
    "cnfa.biophilic.natural_material_ratio": "sam_worker->class_fractions",
    "cnfa.biophilic.greenery_ratio": "sam_worker->class_fractions",
    "cnfa.cognitive.activity_zones_count": "sam_worker->region_count",
    # saliency worker — DeepGaze (research weights) / SR fallback (permissive)
    "cnfa.cognitive.landmark_salience": "deepgaze_worker->peak",
    "cnfa.fluency.figure_ground_clarity": "deepgaze_worker->concentration",
    # memorability worker — ResMem / ViTMem (non-commercial weights)
    "cnfa.cognitive.memorability": "memorability_worker->resmem",
    # aesthetic-score worker — pyiqa NIMA/MUSIQ / TANet (validation signal)
    "cnfa.evaluation.aesthetic_score": "aesthetic_worker->nima",
    "cnfa.evaluation.quality_score": "aesthetic_worker->musiq",
    # material-from-image worker — intrinsic / perceived-gloss (research)
    "cnfa.material.perceived_gloss": "material_worker->gloss",
    "cnfa.material.albedo_mean": "material_worker->albedo",
    "cnfa.material.metallicness": "material_worker->metallic",
}

# --- licence policy ---------------------------------------------------------
POLICIES: Dict[str, set] = {
    # A shipped/commercial build enables permissive only.
    "commercial": {License.PERMISSIVE},
    # A research/validation build may enable everything.
    "research": {License.PERMISSIVE, License.COPYLEFT,
                 License.NONCOMMERCIAL, License.RESEARCH},
}


def select_adapters(
    policy: str = "commercial",
    config: Dict[str, bool] | None = None,
    include_workers: bool = True,
) -> List[AnalyzerAdapter]:
    """Instantiate the adapters allowed by `policy` and switched on by `config`.

    `config` maps each adapter's `enable_flag` to a bool; a flag absent from
    `config` defaults to True (enable-all), matching the repo's canonical
    "enable_all" default.
    """
    allowed = POLICIES[policy]
    config = config or {}
    pool = ALL_ADAPTERS if include_workers else PERMISSIVE_ADAPTERS
    out: List[AnalyzerAdapter] = []
    for cls in pool:
        if cls.license_class not in allowed:
            continue
        if not config.get(cls.enable_flag, True):
            continue
        out.append(cls())
    return out


def run_frame(frame, adapters: Iterable[AnalyzerAdapter]) -> None:
    """Run each adapter over one frame (order-independent; each writes cnfa.*)."""
    for a in adapters:
        a.analyze(frame)
