# Detecção de pose corporal · OpenCV + MediaPipe

Aplicação em Python que acompanha uma pessoa pela webcam e desenha os pontos corporais e as conexões do esqueleto sobre a imagem. Desenvolvida por **Luiz Felipe Steinck**, como etapa inicial dos estudos de estimação de pose que deram origem ao [Monitor STS](https://github.com/FelipeSteinck/projeto-sts).

O detector usa o **MediaPipe Pose Landmarker Lite**, com 33 pontos de referência. O OpenCV captura os quadros, desenha as marcações e exibe a janela. O modelo é pré-treinado e fornecido pelo Google; a contribuição deste projeto está na integração, no tratamento dos pontos e na visualização em tempo real.

## O que aparece na tela

- Pontos vermelhos nas referências corporais visíveis.
- Linhas verdes nas conexões principais dos braços, tronco, pernas e pés.
- Taxa de quadros suavizada em FPS e instrução para encerrar.

A versão atual mantém a visualização sem os avisos “POSE DETECTADA” e “SEM POSE”. Uma pessoa parada também tem uma pose corporal: o programa estima sua posição, sem exigir um gesto ou movimento específico.

## Executar no computador

Ambiente conferido: **Windows, Python 3.11.9**, MediaPipe 0.10.35, OpenCV 5.0.0 e NumPy 2.4.6. É necessário ter webcam e uma sessão com interface gráfica.

Baixe o repositório por **Code → Download ZIP** e extraia a pasta, ou use Git:

```bash
git clone https://github.com/FelipeSteinck/detector-pose-corporal.git
cd detector-pose-corporal
```

No PowerShell, dentro da pasta do projeto:

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe scripts/download_model.py
.\.venv\Scripts\python.exe src/detectar_pose.py
```

O script de preparação baixa o modelo da origem oficial e confere seu tamanho e SHA-256. O binário não precisa ser versionado no repositório.

Clique na janela **Deteccao de pose - linha de base** e pressione **Q** ou **Esc** para encerrar. Se outra aplicação estiver usando a câmera, feche-a antes de iniciar o detector.

## Funcionamento

A webcam fornece quadros ao OpenCV. Cada quadro é convertido de BGR para RGB e enviado ao Pose Landmarker com um instante de tempo crescente. As coordenadas normalizadas retornadas são convertidas para pixels. O desenho considera apenas pontos dentro da imagem e com visibilidade igual ou superior a 0,5; as linhas aparecem quando as duas extremidades estão disponíveis.

A aplicação acompanha **uma pessoa por vez** e solicita captura em 640 × 480. A resolução efetiva e o desempenho dependem da câmera e do computador. O FPS exibido é uma indicação da execução, não um resultado de avaliação de precisão.

## Relação com o Monitor STS

Este repositório apresenta a base de detecção e desenho corporal. O [Monitor STS](https://github.com/FelipeSteinck/projeto-sts) desenvolve a aplicação de sentar e levantar, com calibração, atributos geométricos, classificação das fases, contagem de ciclos completos e exportação CSV. Os dois projetos têm objetivos e instruções próprios.

## Organização

```text
src/detectar_pose.py       Captura, estimação dos pontos e visualização
scripts/download_model.py Preparação e verificação do modelo oficial
models/README.md          Origem e identificação do modelo
docs/DEMONSTRACAO.md      Roteiro de gravação e apresentação
requirements.txt         Dependências do ambiente conferido
REFERENCIAS.md            Bibliotecas e documentação de referência
```

## Demonstração e limites

O programa foi aberto com sucesso no computador de desenvolvimento em 05/11/2026, após a remoção dos avisos de pose. A janela e a inicialização do modelo foram conferidas; não foi realizado um estudo quantitativo de precisão. O vídeo de apresentação será acrescentado quando estiver preparado.

O processamento da webcam ocorre localmente. Este programa não grava vídeo, não captura áudio e não envia quadros para um servidor. Para registrar uma demonstração, use um gravador de tela, conforme o [roteiro](docs/DEMONSTRACAO.md).

Trata-se de um protótipo de estimação de pontos corporais. Ele não identifica exercícios, não conta repetições e não fornece avaliação clínica. Iluminação, enquadramento e oclusões afetam a estimativa.

## Autoria e referências

**Luiz Felipe Steinck** · Engenharia Elétrica, UFSC.

[LinkedIn](https://www.linkedin.com/in/luiz-felipe-steinck/) · [GitHub](https://github.com/FelipeSteinck)

As bibliotecas e o modelo pré-treinado mantêm suas próprias licenças e atribuições. Consulte as [referências](REFERENCIAS.md).
