export interface WebtoonProps {
  id: number
  title: string
  summary: string
}
export interface WebtoonType {
  id: number
  title: string
  summary: string
  genre: string
  thumbnail: string
  webtoon_id: number
  created_by: string
  view: number
  subscribe: number
  grade: number
  released_date: string
  url: string
  cover: string
  likes: number
  sim: number
  social: number
}

export interface WebtoonListProps {
  title: string
  webtoons: WebtoonType[]
}

export interface InputDisplayProps {
  query: string
  genre: string
  nicheness: number
}
