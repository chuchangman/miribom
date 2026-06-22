from django.core.management.base import BaseCommand
from django.db.models import Q
from products.models import Product


class Command(BaseCommand):
    help = '제목·이미지·가격이 없는 불완전 상품을 DB에서 삭제'

    def add_arguments(self, parser):
        parser.add_argument('--dry-run', action='store_true', help='실제 삭제 없이 대상 수만 출력')

    def handle(self, *args, **options):
        incomplete = Product.objects.filter(
            Q(title='') | Q(image='') | Q(lprice__isnull=True) | Q(lprice=0)
        )
        count = incomplete.count()

        if options['dry_run']:
            self.stdout.write(f'삭제 대상 상품: {count}개 (dry-run, 실제 삭제 안 함)')
            return

        incomplete.delete()
        self.stdout.write(self.style.SUCCESS(f'불완전 상품 {count}개 삭제 완료'))
