from core.models import ClubInfo

def club_info(request):
    """
    Ajoute les informations du club à tous les contextes de templates
    """
    try:
        info = ClubInfo.objects.first()
    except:
        info = None

    return {'global_club_info': info}
