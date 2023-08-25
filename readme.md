# N.B.

Скрипт работает по-разному в разных средах.
Я его писал и тестировал на WSL Ubuntu 20.04 без дополнительных библиотек, модулей или утилит.

В "чистом" Google Colab работает.

На Windows 10 не работает.

# Для запуска

```git clone [https]```

Далее в строках 15-20 ввести необходимые данные для почтового сервера (логин и пароль, в случае Яндекса)

```python3 wikipedia_parser start &```

Для остановки

```python3 wikipedia_parser start``` 


### Задача

[test_12_back.pdf](./test_12_back.pdf)

### Мини-эссе
Я расположу по убыванию (по моему мнению) эффективности источников и инструментов для сбора информации.

Помимо Википедии подобного рода информацию можно собирать через RSS-ленты (они все еще довольно активно используются, каталог: ```https://subscribe.ru/catalog/media?rss```) обрабатывая входящие данные по хэш-тэгам или с помощью бинарного классификатора (некролог или нет) и делая саммари через, например ```DeepPavlov```.
Из минусов - и классификатор, и суммаризатор надо обучать. Из плюсов - RSS имеет единый стандарт, как и википедия, и получая данные из разных источников мы их будем получать хотя бы в одном формате.

Так же можно просто парсить сайты СМИ, что гораздо менее эффиективно, чем RSS, так как у каждого сайта своя разметка, хэш-тэги, классы.

Существуют платные инструменты, например Медиалогия, но его эффективность сложнее проверить (и она не гарантирована), в отличии от более простых и дешевых инструментов.

Мониторинг социальных сетей будет менее эффективен из-за большого количества мусора и просто эмоциональных сообщений в случае смерти кого-то близко или важного.
Исключением можно было бы назвать агрегирующие каналы (например в Телеграме). Обычно они избегают публиковать свой материал, но чужой репостят "кластерами" на одну и ту же тему, что может повысить нашу "точность".

Я пытался решить подобную (более простую) задачу с суммаризацией новостной выдачи с упоминанием одного из центров РАН, в нем я адаптировал [это решение](https://github.com/Nikis14/Rus_summarizer), но у меня был ограниченный список сайтов для мониторинга, и под каждый из них было можно настроиться.
Качество же суммаризированного материала было довольно низким - оно падает с увеличением объемов текста.

Здесь же задача с одной стороны проще (ключевых слов не так много "скончался", "погиб" и так далее, с скорее негативным общим настроением и часто повторяющимися именованными сущностями), а с другой - гораздо шире, так как о смерти, например, американского кантри-исполнителя вряд ли напишут российские СМИ.

### [Логика выполнения задачи](./readme_later.md)