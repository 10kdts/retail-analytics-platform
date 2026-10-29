# Row-Level Security

## Cenário demonstrativo

Uma tabela `security_user_region` deve conter `user_email` e `region`. Relacione `region` com `dim_store[region]`.

Expressão do papel `RegionalManager`:

```dax
security_user_region[user_email] = USERPRINCIPALNAME()
```

Para o portfólio, use somente endereços fictícios `example.com`. Teste o papel em **Exibir como** e documente que RLS filtra linhas, mas não substitui permissões de workspace nem governança do gateway.
