/* Otimizações do Banco de Dados */

/* Índices */

-- Tabela unidade
CREATE INDEX idx_unidade_cep ON ldb.public.unidade (cep);
CREATE INDEX idx_unidade_cidade_estado ON ldb.public.unidade (cidade, estado);
-- Justificativa: Índices em 'cep', 'cidade' e 'estado' são úteis para consultas que filtram ou agrupam por localização, melhorando o desempenho de buscas geográficas.

-- Tabela atividade
CREATE INDEX idx_atividade_nome ON ldb.public.atividade (nome_atividade);
-- Justificativa: Acelera buscas por nome de atividade.

-- Tabela facilidade
CREATE INDEX idx_facilidade_nome ON ldb.public.facilidade (nome_facilidade);
-- Justificativa: Acelera buscas por nome de facilidade.

-- Tabela aluno
CREATE INDEX idx_aluno_cpf ON ldb.public.aluno (cpf);
CREATE INDEX idx_aluno_nome ON ldb.public.aluno (nome);
-- Justificativa: Índices em 'cpf' e 'nome' são cruciais para buscas rápidas de alunos, dado que CPF é um identificador único e nome é frequentemente usado em pesquisas.

-- Tabela checkin
CREATE INDEX idx_checkin_unidade_aluno_data ON ldb.public.checkin (id_unidade, id_aluno, data_checkin);
CREATE INDEX idx_checkin_data ON ldb.public.checkin (data_checkin);
-- Justificativa: O índice composto em 'id_unidade', 'id_aluno' e 'data_checkin' otimiza consultas que buscam check-ins por unidade, aluno e período. O índice em 'data_checkin' é vital para consultas baseadas em tempo (diárias/mensais).

-- Tabela status_assinatura
CREATE INDEX idx_status_assinatura_nome ON ldb.public.status_assinatura (nome_status_assinatura);
-- Justificativa: Acelera buscas por nome de status de assinatura.

-- Tabela motivo_cancelamento
CREATE INDEX idx_motivo_cancelamento_descricao ON ldb.public.motivo_cancelamento (descricao_motivo_cancelamento);
-- Justificativa: Acelera buscas por descrição de motivo de cancelamento.

-- Tabela plano
CREATE INDEX idx_plano_nome ON ldb.public.plano (nome_plano);
-- Justificativa: Acelera buscas por nome de plano.

-- Tabela assinatura
CREATE INDEX idx_assinatura_unidade_aluno_plano_status ON ldb.public.assinatura (id_unidade, id_aluno, id_plano, id_status_assinatura);
CREATE INDEX idx_assinatura_data_criacao ON ldb.public.assinatura (data_criacao);
CREATE INDEX idx_assinatura_data_vigencia ON ldb.public.assinatura (data_vigencia);
-- Justificativa: Índices em chaves estrangeiras e datas são essenciais para otimizar joins e filtros em consultas de assinaturas, como as que envolvem planos e status.

-- Tabela solicitacao_cancelamento
CREATE INDEX idx_solicitacao_cancelamento_assinatura_motivo_data ON ldb.public.solicitacao_cancelamento (id_assinatura, id_motivo_cancelamento, data_solicitacao);
-- Justificativa: Otimiza consultas que buscam solicitações de cancelamento por assinatura, motivo e data.

-- Tabela status_cobranca
CREATE INDEX idx_status_cobranca_nome ON ldb.public.status_cobranca (nome_status_cobranca);
-- Justificativa: Acelera buscas por nome de status de cobrança.

-- Tabela cobranca
CREATE INDEX idx_cobranca_assinatura_status_data ON ldb.public.cobranca (id_assinatura, id_status_cobranca, data_criacao, data_vencimento);
-- Justificativa: Otimiza consultas que envolvem assinaturas, status e datas de cobrança.

-- Tabela pagamento
CREATE INDEX idx_pagamento_cobranca_data ON ldb.public.pagamento (id_cobranca, data_pagamento);
-- Justificativa: Otimiza consultas que buscam pagamentos por cobrança e data.

-- Tabela pagamento_cartao_credito
CREATE INDEX idx_pagamento_cartao_credito_final_cartao ON ldb.public.pagamento_cartao_credito (final_cartao);
-- Justificativa: Acelera buscas por final de cartão de crédito.

-- Tabela pagamento_pix
CREATE INDEX idx_pagamento_pix_chave_pix ON ldb.public.pagamento_pix (chave_pix);
-- Justificativa: Acelera buscas por chave pix.





