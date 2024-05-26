# Image2Latex
Распознавание текста и перевод его в LaTex

## Запуск работы с моделью
1) Скачайте файл best.pt.
2) Скачайте датасет.
3) В папке проекта должны лежать:
   - папка с датасетом строго с названием dataset (без него ругается YOLO)
   - файл best.pt
   - файл data.yaml (его можно просто создать перед началом работы, кусок для этого закомментирован)
   
## Модель от 05.03.2024
https://drive.google.com/drive/folders/1SRGZdzGqXhf1FumgEneTKJ5_sjuIzepK?usp=sharing

                 Class     Images  Instances      Box(P          R      mAP50  mAP50-95): 100%|██████████| 2/2 [01:12<00:00, 36.47s/it]
                   all         25       1530       0.82      0.864      0.864      0.584
               formula         25        614      0.776      0.786      0.807        0.5
                  text         25        896      0.825      0.805       0.84      0.567
               picture         25         20      0.858          1      0.944      0.684

## Модель от 15.03.2024
https://drive.google.com/drive/folders/1bm-AOOOSzFWYWTpVWIN3h1yOpKRD1ELT?usp=sharing

                 Class     Images  Instances      Box(P          R      mAP50  mAP50-95): 100%|██████████| 7/7 [03:40<00:00, 31.45s/it]
                   all        101       4937      0.822      0.814      0.833      0.578
               formula        101       1813      0.817      0.779      0.814      0.522
                  text        101       3028      0.837      0.801      0.837      0.562
               picture        101         96      0.813      0.863      0.847       0.65

## Модель от 15.04.2024
https://drive.google.com/drive/folders/1HJCQzFCj7rao82gh8fFTK9U1kUF4RH6o?usp=sharing

                 Class     Images  Instances      Box(P          R      mAP50  mAP50-95): 100%|██████████| 13/13 [04:32<00:00, 20.97s/it]
                   all        197      10050      0.799       0.83      0.829       0.56
               formula        197       3869      0.841      0.836      0.865      0.554
                  text        197       5996      0.852      0.865      0.889      0.593
               picture        197        185      0.705      0.789      0.733      0.534
