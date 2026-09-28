# Math Runner

Jogo educacional 2D em Pygame, organizado no mesmo formato simples de `subaquatica`:

- `main.py`: inicializacao e loop principal.
- `scripts/entities.py`: corredor e respostas nas faixas.
- `scripts/scenes.py`: fases, questoes, pontuacao, telas e ranking.
- `scripts/ui.py`: funcoes pequenas de interface.
- `assets/`: imagens opcionais do personagem e do fundo.

## Executar

```bash
python -m pip install -r requirements.txt
python main.py
```

Na tela inicial, digite o apelido, pressione Enter para jogar ou R para abrir o ranking. Durante a corrida, use as setas esquerda e direita para escolher uma faixa; Esc pausa. A resposta deve estar na faixa do corredor quando o portao chegar a linha de decisao.

As cinco fases cobrem adicao e subtracao, multiplicacao, divisao e fracoes simples, equacoes de primeiro grau e um desafio misturado mais rapido. Acertos somam pontos, a sequencia aumenta o bonus e concluir fases concede pontos extras. Erro ou tempo esgotado encerra a partida.

As dez melhores pontuacoes ficam em `ranking.json`, criado automaticamente ao terminar uma partida. O GDD menciona persistencia e ranking via Django, mas nao define URL, autenticacao ou formato da API. Por isso esta versao funciona sem servidor e concentra o salvamento num unico metodo (`save_score`) para facilitar a futura conexao ao backend.

O visual agora usa uma pista arcade clara, cores quentes, faixas pastel e simbolos matematicos. O personagem usa `assets/jogadora (2).png`; para adicionar um fundo ou substituir a arte, veja `assets/README.md`.
