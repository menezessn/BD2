create database ldb;

create table ldb.public.unidade (
    id_unidade INT primary key,
    cep CHAR(8) not null,
    logradouro text not null,
    numero text,
    complemento text,
    cidade text not null,
    estado text not null
);

create table ldb.public.atividade (
    id_atividade int primary key,
    nome_atividade text not null
);

create table ldb.public.facilidade (
    id_facilidade int primary key,
    nome_facilidade text not null
);

create table ldb.public.unidade_atividade (
    id_unidade int not null,
    id_atividade int not null,
    PRIMARY KEY (id_unidade, id_atividade),
    FOREIGN KEY (id_unidade) REFERENCES unidade (id_unidade),
    FOREIGN KEY (id_atividade) REFERENCES atividade (id_atividade)
);

create table ldb.public.unidade_facilidade (
    id_unidade int not null,
    id_facilidade int not null,
    PRIMARY KEY (id_unidade, id_facilidade),
    FOREIGN KEY (id_unidade) REFERENCES unidade (id_unidade),
    FOREIGN KEY (id_facilidade) REFERENCES facilidade (id_facilidade)
);

create table ldb.public.aluno (
    id_aluno int primary key,
    cpf char(11) not null,
    nome text not null
);

create table ldb.public.checkin (
    id_checkin int primary key,
    id_unidade int not null,
    id_aluno int not null,
    data_checkin date not null,
    FOREIGN KEY (id_unidade) REFERENCES unidade (id_unidade),
    FOREIGN KEY (id_aluno) REFERENCES aluno (id_aluno)
);

create table ldb.public.status_assinatura(
    id_status_assinatura int primary key,
    nome_status_assinatura text not null
);

create table ldb.public.motivo_cancelamento(
    id_motivo_cancelamento int primary key,
    descricao_motivo_cancelamento text not null
);

create table ldb.public.plano(
    id_plano int primary key,
    nome_plano text not null
);

create table ldb.public.assinatura (
    id_assinatura int primary key,
    id_unidade int not null,
    id_aluno int not null,
    id_plano int not null,
    id_status_assinatura int not null,
    data_criacao date not null,
    data_vigencia date not null,
    FOREIGN KEY (id_unidade) REFERENCES unidade (id_unidade),
    FOREIGN KEY (id_aluno) REFERENCES aluno (id_aluno),
    FOREIGN KEY (id_plano) REFERENCES plano (id_plano),
    FOREIGN KEY (id_status_assinatura) REFERENCES status_assinatura (id_status_assinatura)
);

create table ldb.public.solicitacao_cancelamento (
    id_solicitacao_cancelamento int,
    id_assinatura int not null,
    id_motivo_cancelamento int not null,
    data_solicitacao date not null,
    PRIMARY KEY (id_solicitacao_cancelamento, id_assinatura),
    FOREIGN KEY (id_assinatura) REFERENCES assinatura (id_assinatura),
    FOREIGN KEY (id_motivo_cancelamento) REFERENCES motivo_cancelamento (id_motivo_cancelamento)
);

create table ldb.public.status_cobranca (
    id_status_cobranca int primary key,
    nome_status_cobranca text not null
);

create table ldb.public.cobranca (
    id_cobranca int primary key,
    id_assinatura int not null,
    data_criacao date not null,
    data_vencimento date not null,
    valor float not null,
    id_status_cobranca int not null,
    FOREIGN KEY (id_assinatura) REFERENCES assinatura (id_assinatura),
    FOREIGN KEY (id_status_cobranca) REFERENCES status_cobranca (id_status_cobranca)
);

create table ldb.public.pagamento (
    id_pagamento int primary key,
    data_pagamento date not null,
    id_cobranca int not null,
    FOREIGN KEY (id_cobranca) REFERENCES cobranca (id_cobranca)
);

create table ldb.public.pagamento_cartao_credito (
    id_pagamento int primary key,
    final_cartao char(4) not null,
    FOREIGN KEY (id_pagamento) REFERENCES pagamento (id_pagamento)
);

create table ldb.public.pagamento_pix (
    id_pagamento int primary key,
    chave_pix text not null,
    FOREIGN KEY (id_pagamento) REFERENCES pagamento (id_pagamento)
);

-- CREATE OR REPLACE FUNCTION check_max_pagamentos_cobranca()
-- RETURNS TRIGGER AS $$
-- DECLARE
--     pagamentos_existentes INT;
-- BEGIN
--     SELECT COUNT(*)
--     INTO pagamentos_existentes
--     FROM ldb.public.pagamento
--     WHERE id_cobranca = NEW.id_cobranca;

--     IF pagamentos_existentes >= 1 THEN
--         RAISE EXCEPTION 'A cobrança com ID % já possui um pagamento associado e não pode receber outro.', NEW.id_cobranca;
--     END IF;

--     RETURN NEW;
-- END;
-- $$ LANGUAGE plpgsql;

-- CREATE TRIGGER tg_check_max_pagamentos
--     BEFORE INSERT ON ldb.public.pagamento
--     FOR EACH ROW
--     EXECUTE FUNCTION check_max_pagamentos_cobranca();

-- CREATE OR REPLACE FUNCTION atualiza_status_cobranca() RETURNS TRIGGER AS $$
-- BEGIN
--     UPDATE ldb.public.cobranca
--     SET id_status_cobranca = 2
--     WHERE id_cobranca = NEW.id_cobranca;

--     RETURN NEW;
-- END;
-- $$ LANGUAGE plpgsql;

-- CREATE TRIGGER tg_atualiza_status_cobranca
--     AFTER INSERT ON pagamento
--     FOR EACH ROW
--     EXECUTE FUNCTION atualiza_status_cobranca();

-- CREATE OR REPLACE FUNCTION validar_checkin_assinatura_ativa()
-- RETURNS TRIGGER AS $$
-- DECLARE
--     assinatura_valida INT;
-- BEGIN
--     SELECT COUNT(*)
--     INTO assinatura_valida
--     FROM ldb.public.assinatura a
--     WHERE 
--         a.id_aluno = NEW.id_aluno
--         AND a.id_unidade = NEW.id_unidade
--         AND a.id_status_assinatura = 1 -- status 'ativa'
--         AND NEW.data_checkin BETWEEN a.data_criacao AND a.data_vigencia;

--     IF assinatura_valida = 0 THEN
--         RAISE EXCEPTION 'Check-in inválido: o aluno % não possui assinatura ativa na unidade % na data %.',
--             NEW.id_aluno, NEW.id_unidade, NEW.data_checkin;
--     END IF;

--     RETURN NEW;
-- END;
-- $$ LANGUAGE plpgsql;

-- CREATE TRIGGER tg_validar_checkin_assinatura
-- BEFORE INSERT ON ldb.public.checkin
-- FOR EACH ROW
-- EXECUTE FUNCTION validar_checkin_assinatura_ativa();