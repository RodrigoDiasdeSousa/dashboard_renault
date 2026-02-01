from django.db import models

class SurveyResponse(models.Model):
    source = models.CharField("Origem", max_length=50)
    date = models.DateField("Data da Resposta", null=True, blank=True)
    location_name = models.CharField("Nome/ID Loja", max_length=255)
    
    customer_name = models.CharField("Cliente", max_length=255, null=True, blank=True)
    model = models.CharField("Modelo", max_length=100, null=True, blank=True)
    
    # --- AS 3 NOTAS DO NPS (Escala 1-5) ---
    score_general = models.IntegerField("Nota Geral", null=True, blank=True)
    score_delivery = models.IntegerField("Nota Entrega", null=True, blank=True)
    score_consultant = models.IntegerField("Nota Consultor", null=True, blank=True)
    
    comment = models.TextField("Comentário", null=True, blank=True)

    def __str__(self):
        return f"{self.location_name} - Geral: {self.score_general}"