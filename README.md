# Waipe · IVAN ALEX MANDUCA

Agentes (flows do Waipe Flow) e páginas (plugins do Waipe Páginas) deste cliente, versionados com o framework `waipe-template`.

- Cada agente fica em `agentes/<slug>/` com o `.json` (para importar) e o `.md` (documentação).
- Cada página fica em `plugins/<slug>/` com o `.json` (para instalar no Waipe Páginas), o `.md` e o `exemplo.json`.
- Modelos para começar: `modelos/agentes/` e `modelos/plugins/` (vêm do framework).
- Uma branch só, `main`: o que está nela é a versão em trabalho, que você importa e testa.
- Versões fechadas: aba **Releases** (agente: tag `<slug>/vX.Y.Z`; página: tag `plugins/<slug>/vX.Y.Z`).
- Como trabalhar: `.claude/waipe/LEIAME.md`.
