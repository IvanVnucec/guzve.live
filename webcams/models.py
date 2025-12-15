from django.db import models

class Category(models.Model):
    key = models.CharField(max_length=16, primary_key=True)
    seokey = models.CharField(max_length=128)
    name = models.CharField(max_length=128)
    icon_url = models.URLField(max_length=128)

    class Meta:
        verbose_name_plural = "Categories"

    def __str__(self) -> str:
        return self.name

class Group(models.Model):
    key = models.CharField(max_length=128, primary_key=True)
    title = models.CharField(max_length=128)
    lat = models.FloatField()
    lon = models.FloatField()
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='groups')

    def __str__(self) -> str:
        return self.title

class Webcam(models.Model):
    id = models.PositiveIntegerField(primary_key=True)
    title = models.CharField(max_length=128)
    last_update = models.DateTimeField()
    heading = models.PositiveIntegerField(blank=True, null=True)
    refresh_delay = models.PositiveIntegerField()
    map_radius = models.PositiveIntegerField()
    lat = models.FloatField()
    lon = models.FloatField()
    image_width = models.PositiveIntegerField()
    image_height = models.PositiveIntegerField()
    group = models.ForeignKey(Group, on_delete=models.CASCADE, related_name='webcams')

    def __str__(self) -> str:
        return self.title

    @property
    def image_url(self) -> str:
        return f"https://api.hak.hr/rest/2.8/webcams/{self.id}/?token=9ba354b85afbd2"

class CongestionEstimate(models.Model):
    webcam = models.ForeignKey(Webcam, on_delete=models.CASCADE, related_name='congestion_est')
    datetime = models.DateTimeField()
    num_vehicles = models.PositiveIntegerField()
    score = models.PositiveIntegerField()

    def __str__(self):
        return f"{self.webcam.title} @ {self.datetime.strftime("%d/%m/%Y, %H:%M:%S")}: {self.num_vehicles}, {self.score}/10"
