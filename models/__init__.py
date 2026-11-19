"""Modelos e regras de domínio do sistema hospitalar."""

from .usuario import UsuarioRepository
from .paciente import Paciente, PacienteManager, SQLitePacienteRepository

# Exporta as classes de domínio usadas pelos módulos da aplicação.
__all__ = ["UsuarioRepository", "Paciente", "PacienteManager", "SQLitePacienteRepository"]
