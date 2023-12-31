// Represents the structure of a user profile object received from the API.
export interface UserProfileResponse {
  bio: string;
  can_view: boolean;
  follow_status: string | boolean;
  num_followers: number;
  num_following: number;
  num_posts: number;
  posts: Array<{
    id: number;
    media: string;
    like_count: number;
    comment_count: number;
  }>;
  profile_picture: string | null;
  username: string;
  first_name: string | null;
  last_name: string | null;
  pagination: {
    next: string | null;
    previous: string | null;
  };
}
