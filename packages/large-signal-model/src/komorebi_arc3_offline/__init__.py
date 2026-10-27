"""Komorebi PR-LASM: an offline projector-resolved large signal model."""

from .agent import AgentConfig, OfflineBayesianOperatorAgent
from .exact_atlas import AtlasAnalysis, MultiAtlasAnalyzer, MultiAtlasConfig
from .lasm_agent import UltimateAgentConfig, UltimateLargeSignalAgent
from .lasm_model import ProjectorResolvedLargeSignalModel
from .lasm_packetizer import LASMPacketizerConfig, UltimateLASMPacketizer
from .model import BayesianOperatorWorldModel
from .offline_guard import OfflineNetworkError, assert_offline_guard, install_offline_guard
from .packetizer import FramePacketizer, PacketizerConfig

__all__ = [
    "AgentConfig",
    "AtlasAnalysis",
    "BayesianOperatorWorldModel",
    "FramePacketizer",
    "LASMPacketizerConfig",
    "MultiAtlasAnalyzer",
    "MultiAtlasConfig",
    "OfflineBayesianOperatorAgent",
    "OfflineNetworkError",
    "PacketizerConfig",
    "ProjectorResolvedLargeSignalModel",
    "UltimateAgentConfig",
    "UltimateLASMPacketizer",
    "UltimateLargeSignalAgent",
    "assert_offline_guard",
    "install_offline_guard",
]

__version__ = "2.3.0"
__author__ = "Komorebi P."
