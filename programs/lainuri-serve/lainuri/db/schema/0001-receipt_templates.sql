CREATE TABLE receipt_templates (
  id INTEGER PRIMARY KEY ASC,
  type TEXT NOT NULL,
  locale_code TEXT NOT NULL,
  template TEXT NOT NULL
);
CREATE UNIQUE INDEX receipt_templates_unique_type_locale ON receipt_templates (type, locale_code);

INSERT INTO receipt_templates VALUES
   (NULL,'checkin','en','
<body>
  {{ header }}
  <h4>Returns {{ today }}</h4>
  <ul>
  {% for item in items %}
    <li>{{ item.title }}, {{ item.author }} : {{ item.item_barcode }}</li>
  {% endfor %}
  </ul>
  {{ footer }}
</body>
'),(NULL,'checkin','fi','
<body>
  {{ header }}
  <h4>Palautuksesi {{ today }}</h4>
  <ul>
  {% for item in items %}
    <li>{{ item.title }}, {{ item.author }} : {{ item.item_barcode }}</li>
  {% endfor %}
  </ul>
  {{ footer }}
</body>
'),(NULL,'checkin','ru','
<body>
  {{ header }}
  <h4>Ваши возвращения {{ today }}</h4>
  <ul>
  {% for item in items %}
    <li>{{ item.title }}, {{ item.author }} : {{ item.item_barcode }}</li>
  {% endfor %}
  </ul>
  {{ footer }}
</body>
'),(NULL,'checkin','sv','
<body>
  {{ header }}
  <h4>Dina checkins {{ today }}</h4>
  <ul>
  {% for item in items %}
    <li>{{ item.title }}, {{ item.author }} : {{ item.item_barcode }}</li>
  {% endfor %}
  </ul>
  {{ footer }}
</body>
'),(NULL,'checkout','en','
<body>
  {{ header }}
  <h4>Your loans {{ today }}</h4>
  <ul>
  {% for item in items %}
    <li>{{ item.title }}, {{ item.author }} : {{ item.item_barcode }}</li>
  {% endfor %}
  </ul>
  {{ footer }}
</body>
'),(NULL,'checkout','fi','
<body>
  {{ header }}
  <h4>Lainasi {{ today }}</h4>
  <ul>
  {% for item in items %}
    <li>{{ item.title }}, {{ item.author }} : {{ item.item_barcode }}</li>
  {% endfor %}
  </ul>
  {{ footer }}
</body>
'),(NULL,'checkout','ru','
<body>
  {{ header }}
  <h4>Ваши кредиты {{ today }}</h4>
  <ul>
  {% for item in items %}
    <li>{{ item.title }}, {{ item.author }} : {{ item.item_barcode }}</li>
  {% endfor %}
  </ul>
  {{ footer }}
</body>
'),(NULL,'checkout','sv','
<body>
  {{ header }}
  <h4>Dina utcheckningar {{ today }}</h4>
  <ul>
  {% for item in items %}
    <li>{{ item.title }}, {{ item.author }} : {{ item.item_barcode }}</li>
  {% endfor %}
  </ul>
  {{ footer }}
</body>
');
