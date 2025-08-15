# AudioBom 1.0

**AudioBom** é um processador de áudio gratuito e de código aberto, feito para facilitar o tratamento de arquivos de voz para rádios, podcasts e gravações caseiras.

## Funcionalidades
- Conversão automática para estéreo e 44.1kHz
- Compressão, equalização e de-essing (via FFmpeg)
- Normalização de loudness para -16 LUFS
- Limitação de picos a -6 dBFS
- Exportação em MP3 192kbps
- Interface gráfica simples e intuitiva

## Como usar
1. Abra o programa (`AudioBom.exe`)
2. Escolha a pasta de áudios brutos (originais)
3. Escolha a pasta de destino para os áudios processados
4. Selecione os arquivos desejados
5. (Opcional) Ouça uma prévia dos arquivos
6. Clique em "Executar" e aguarde o processamento

Veja o arquivo [`MANUAL.txt`](MANUAL.txt) para instruções detalhadas para usuários leigos.

## Requisitos
- Windows 10 ou superior
- Não requer instalação de Python ou FFmpeg (já incluídos no pacote)

## Como empacotar (para desenvolvedores)
1. Instale as dependências:
   ```
   pip install -r requirements.txt
   ```
2. Gere o executável com o PyInstaller:
   ```
   pyinstaller audiobom.spec
   ```
3. O executável estará na pasta `dist/AudioBom/`

## Créditos
- Desenvolvido por Daniel Ito Isaia
- Utiliza [FFmpeg](https://ffmpeg.org/), [PyDub](https://github.com/jiaaro/pydub), [pygame](https://www.pygame.org/), [pyloudnorm](https://github.com/csteinmetz1/pyloudnorm)

## Licença
Este projeto é livre para uso e distribuição.