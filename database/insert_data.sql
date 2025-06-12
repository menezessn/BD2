-- Populando status e planos básicos
INSERT INTO ldb.public.status_assinatura VALUES (1, 'Ativa'), (2, 'Cancelada');
INSERT INTO ldb.public.status_cobranca VALUES (1, 'Pendente'), (2, 'Paga');
INSERT INTO ldb.public.plano VALUES (1, 'Mensal'), (2, 'Trimestral'), (3, 'Anual');

-- Populando unidades (ex: 50 unidades)
INSERT INTO ldb.public.unidade (id_unidade, cep, logradouro, numero, complemento, cidade, estado)
SELECT i, '01001000', 'Rua Teste', i::text, NULL, 'São Paulo', 'SP'
FROM generate_series(1, 50) AS i;

-- Populando atividades e facilidades (10 de cada)
INSERT INTO ldb.public.atividade SELECT i, 'Atividade ' || i FROM generate_series(1, 10) AS i;
INSERT INTO ldb.public.facilidade SELECT i, 'Facilidade ' || i FROM generate_series(1, 10) AS i;

-- Relacionando cada unidade com 3 atividades e 3 facilidades aleatórias
INSERT INTO ldb.public.unidade_atividade
SELECT u.id_unidade, (random() * 9 + 1)::int
FROM ldb.public.unidade u, generate_series(1, 3);

INSERT INTO ldb.public.unidade_facilidade
SELECT u.id_unidade, (random() * 9 + 1)::int
FROM ldb.public.unidade u, generate_series(1, 3);

-- Populando 100.000 alunos
INSERT INTO ldb.public.aluno (id_aluno, cpf, nome)
SELECT i, lpad(i::text, 11, '0'), 'Aluno ' || i
FROM generate_series(1, 100000) AS i;

-- Populando 100.000 assinaturas (um aluno por assinatura)
INSERT INTO ldb.public.assinatura (
    id_assinatura, id_unidade, id_aluno, id_plano, id_status_assinatura, data_criacao, data_vigencia
)
SELECT i,
       (random() * 49 + 1)::int, -- unidade entre 1 e 50
       i,
       (random() * 2 + 1)::int, -- plano entre 1 e 3
       1, -- status ativa
       CURRENT_DATE - (random() * 365)::int,
       CURRENT_DATE + (random() * 365)::int
FROM generate_series(1, 100000) AS i;

-- Populando 1.000.000 check-ins com alunos e unidades consistentes
INSERT INTO ldb.public.checkin (id_checkin, id_unidade, id_aluno, data_checkin)
SELECT i,
       a.id_unidade,
       a.id_aluno,
       CURRENT_DATE - (random() * 30)::int
FROM generate_series(1, 1000000) AS i
JOIN ldb.public.assinatura a ON a.id_assinatura = ((random() * 99999 + 1)::int);

-- Populando 200.000 cobranças (2 por aluno)
INSERT INTO ldb.public.cobranca (id_cobranca, id_assinatura, data_criacao, data_vencimento, valor, id_status_cobranca)
SELECT i,
       (random() * 99999 + 1)::int,
       CURRENT_DATE - (random() * 60)::int,
       CURRENT_DATE + (random() * 30)::int,
       (random() * 100 + 50)::numeric(6,2),
       CASE WHEN random() > 0.5 THEN 1 ELSE 2 END
FROM generate_series(1, 200000) AS i;

-- Populando 100.000 pagamentos para cobranças com status = 2 (paga)
INSERT INTO ldb.public.pagamento (id_pagamento, data_pagamento, id_cobranca)
SELECT i,
       CURRENT_DATE - (random() * 20)::int,
       c.id_cobranca
FROM (
    SELECT id_cobranca FROM ldb.public.cobranca WHERE id_status_cobranca = 2 LIMIT 100000
) AS c
JOIN generate_series(1, 100000) AS i ON TRUE;

-- Pagamentos via cartão
INSERT INTO ldb.public.pagamento_cartao_credito (id_pagamento, final_cartao)
SELECT id_pagamento, lpad(((random() * 9999)::int)::text, 4, '0')
FROM ldb.public.pagamento WHERE random() > 0.5;

-- Pagamentos via pix
INSERT INTO ldb.public.pagamento_pix (id_pagamento, chave_pix)
SELECT id_pagamento, 'chave-' || id_pagamento
FROM ldb.public.pagamento WHERE id_pagamento NOT IN (SELECT id_pagamento FROM ldb.public.pagamento_cartao_credito);

-- Populando 10.000 solicitações de cancelamento
INSERT INTO ldb.public.motivo_cancelamento (id_motivo_cancelamento, descricao_motivo_cancelamento)
SELECT i, 'Motivo ' || i FROM generate_series(1, 10) AS i;

INSERT INTO ldb.public.solicitacao_cancelamento (
    id_solicitacao_cancelamento, id_assinatura, id_motivo_cancelamento, data_solicitacao
)
SELECT i,
       (random() * 99999 + 1)::int,
       (random() * 9 + 1)::int,
       CURRENT_DATE - (random() * 60)::int
FROM generate_series(1, 10000) AS i;
