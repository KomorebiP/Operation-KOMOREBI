"""Public API for the Projector-Resolved Large Algebraic Signal Model."""

from komorebi_arc3_offline.exact_atlas import (
    AtlasAnalysis,
    MultiAtlasAnalyzer,
    MultiAtlasConfig,
    color_one_hot,
    fourier_band_masks,
    fourier_project,
    haar2d_forward,
    haar2d_inverse,
    polyphase2d_analyze,
    polyphase2d_synthesize,
    polyphase_project,
    reconstruct_color,
    wavelet_project,
    wavelet_subband_slices,
)
from komorebi_arc3_offline.lasm_agent import UltimateAgentConfig, UltimateLargeSignalAgent
from komorebi_arc3_offline.lasm_graph import StateTransitionGraph, TransitionStats
from komorebi_arc3_offline.lasm_memory import LASMMemory, LASMRoleStatistics
from komorebi_arc3_offline.lasm_model import FittedLASMProgram, ProjectorResolvedLargeSignalModel
from komorebi_arc3_offline.lasm_packetizer import LASMPacketizerConfig, UltimateLASMPacketizer
from komorebi_arc3_offline.lasm_programs import LASMProgram, default_lasm_programs
from komorebi_arc3_offline.lasm_refinement import (
    BestBasisResult,
    PacketTree,
    best_basis,
    haar_pair_analyze,
    haar_pair_synthesize,
    l1_packet_cost,
    pruning_feature_vector,
    shannon_packet_cost,
)
from komorebi_arc3_offline.lasm_types import (
    GraphEdge,
    LASMFramePackets,
    LASMPrediction,
    LASMRunTrace,
    LASMTransition,
)
from komorebi_arc3_offline.offline_guard import (
    OfflineNetworkError,
    assert_offline_guard,
    install_offline_guard,
)

__version__ = "2.1.0"
__author__ = "Komorebi P."

__all__ = [
    "AtlasAnalysis",
    "BestBasisResult",
    "FittedLASMProgram",
    "GraphEdge",
    "LASMFramePackets",
    "LASMMemory",
    "LASMPacketizerConfig",
    "LASMPrediction",
    "LASMProgram",
    "LASMRoleStatistics",
    "LASMRunTrace",
    "LASMTransition",
    "MultiAtlasAnalyzer",
    "MultiAtlasConfig",
    "OfflineNetworkError",
    "PacketTree",
    "ProjectorResolvedLargeSignalModel",
    "StateTransitionGraph",
    "TransitionStats",
    "UltimateAgentConfig",
    "UltimateLASMPacketizer",
    "UltimateLargeSignalAgent",
    "assert_offline_guard",
    "best_basis",
    "color_one_hot",
    "default_lasm_programs",
    "fourier_band_masks",
    "fourier_project",
    "haar2d_forward",
    "haar2d_inverse",
    "haar_pair_analyze",
    "haar_pair_synthesize",
    "install_offline_guard",
    "l1_packet_cost",
    "polyphase2d_analyze",
    "polyphase2d_synthesize",
    "polyphase_project",
    "pruning_feature_vector",
    "reconstruct_color",
    "shannon_packet_cost",
    "wavelet_project",
    "wavelet_subband_slices",
]
