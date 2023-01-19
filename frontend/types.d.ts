interface BaseApiResponse {
  query_time: number;
  count: number;
}

interface Work {
  block_time: string;
  venue_id: string;
  mnky: boolean;
  venue_owner: string;
  user: string;
}

interface WorkApiResponse extends BaseApiResponse {
  data: Work[];
}

interface Drop {
  issue_time: string;
  type: string;
  winners: string[];
  trx_id: string;
  state: string;
}

interface DropsApiResponse extends BaseApiResponse {
  data: Drop[];
}

interface CMCApiResponse extends BaseApiResponse {
  data: string[];
}
