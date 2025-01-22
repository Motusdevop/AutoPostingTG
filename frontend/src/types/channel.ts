export interface Channel {
  id: number;
  name: string;
  chat_id: number;
  parse_mode: string;
  interval: number;
  path_to_source_dir: string;
  path_to_done_dir: string;
  path_to_except_dir: string;
  active: boolean;
}

export interface NewChannel {
  name: string;
  chat_id: number;
  parse_mode: string;
  interval: number;
}

export interface Channels {
  channels: Channel[];
}