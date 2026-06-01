import defaultProductImage from './default-products.png'

const mockVideos = [
  {
    id: '1',
    videoUploadId: '1',
    productId: '1',
    userId: '1',

    videoUrl: '',
    thumbnailUrl: defaultProductImage,
    status: 'completed',

    productName: '세탁기',
    productBrand: '삼성',
    category: '세탁·건조',

    rating: 5,
    reviewContent: '원룸에서 사용해도 소음이 크지 않고 크기도 적당했습니다.',

    userNickname: '자취3년차',
    userHousingType: '원룸',
    userAreaSize: 7,

    likeCount: 12,
    isLiked: true,

    createdAt: '2026-05-31',
  },
  {
    id: '2',
    videoUploadId: '2',
    productId: '2',
    userId: '2',

    videoUrl: '',
    thumbnailUrl: defaultProductImage,
    status: 'completed',

    productName: '건조기',
    productBrand: 'LG',
    category: '세탁·건조',

    rating: 4,
    reviewContent: '건조 시간은 만족스럽지만 좁은 공간에서는 배치 위치를 잘 봐야 합니다.',

    userNickname: '원룸러',
    userHousingType: '원룸',
    userAreaSize: 6,

    likeCount: 8,
    isLiked: false,

    createdAt: '2026-05-30',
  },
  {
    id: '3',
    videoUploadId: '3',
    productId: '3',
    userId: '3',

    videoUrl: '',
    thumbnailUrl: defaultProductImage,
    status: 'completed',

    productName: '냉장고',
    productBrand: '삼성',
    category: '냉장고',

    rating: 5,
    reviewContent: '문 열리는 공간까지 보면 생각보다 자리를 많이 차지합니다.',

    userNickname: '오피스텔거주자',
    userHousingType: '오피스텔',
    userAreaSize: 10,

    likeCount: 21,
    isLiked: true,

    createdAt: '2026-05-29',
  },
]

export default mockVideos
