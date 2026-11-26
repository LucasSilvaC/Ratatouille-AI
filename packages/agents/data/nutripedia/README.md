# Dados da Nutripédia

Os PDFs da bibliografia e o índice gerado a partir deles **não vão para o Git**: alguns
artigos têm direitos autorais e o índice é recriado a partir dos PDFs. Esta pasta guarda
só esta lista.

| Pasta     | Conteúdo                                                     | No Git? |
| --------- | ------------------------------------------------------------ | ------- |
| `pdfs/`   | Os PDFs da bibliografia (copie da pasta do Drive do grupo)   | Não     |
| `indice/` | `trechos.json` e `vetores.npy`, gerados na primeira execução | Não     |

Para usar outra pasta, defina `NUTRIPEDIA_DADOS` com o caminho que contém `pdfs/` e `indice/`.
Ao adicionar ou trocar PDFs, apague `indice/` para que o índice seja recriado.

## Bibliografia usada na avaliação atual

1. Ministério da Saúde. _Guia alimentar para a população brasileira_, 2ª ed., 2014.
2. Ministério da Saúde. _Guia de bolso sobre alimentação_.
3. _Diagnosis and management of food allergy_ (artigo em inglês).
4. Eliane Aparecida da Silva Francisconi: trabalho sobre doença celíaca e glúten.
5. _Em Foco_ 02.17: substituição da farinha de trigo na dieta sem glúten.
6. _Importância dos alimentos no controle glicêmico dos indivíduos com diabetes mellitus tipo 2: uma revisão da literatura_ (2018).
7. _Benefícios dos alimentos funcionais na prevenção do diabetes mellitus_: PDF escaneado,
   sem texto extraível; fica de fora do índice até passar por OCR.

O índice atual tem 1.067 trechos dos 6 PDFs com texto.
