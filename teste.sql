SELECT 
    DATE_TRUNC('month', data_checkin) as month,
    COUNT(DISTINCT id_aluno) as alunos
FROM checkin
GROUP BY month

SELECT COUNT(DISTINCT id_aluno) as alunos
FROM aluno