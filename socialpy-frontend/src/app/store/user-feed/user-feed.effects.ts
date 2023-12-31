import { Injectable } from '@angular/core';

import { Actions, createEffect, ofType } from '@ngrx/effects';
import { select, Store } from '@ngrx/store';

import {
  catchError,
  switchMap,
  mergeMap,
  withLatestFrom,
} from 'rxjs/operators';
import { of } from 'rxjs';

import { UserService } from 'src/app/api-services/user/user.service';

import * as UserFeedActions from 'src/app/store/user-feed/user-feed.actions';
import * as PostActions from 'src/app/store/post-actions/post-actions.actions';
import { Post } from '../../interface-types/user-feed.model';

import { selectLikedPostIds } from '../selectors/post-actions.selector';
import { AppState } from '../app.state';

@Injectable()
export class UserFeedEffects {
  constructor(
    private actions$: Actions,
    private userService: UserService,
    private store: Store<AppState>
  ) {}

  // Effect middleware function to load the user's feed when the 'loadUserFeed' action is called
  // The function obtains the user's feed data from the api and updates the selectLikedPostIds state to
  // add any unique posts obtained from the feed that have already been liked by the user
  loadUserFeed$ = createEffect(() =>
    this.actions$.pipe(
      ofType(UserFeedActions.loadUserFeed), // Listen for the 'loadUserFeed' action
      switchMap((action) =>
        // Fetch the user's feed from the userService API
        this.userService.getUserFeed(action.page).pipe(
          // Combine the result of the API call with selectLikedPostIds selector obtained from the store
          withLatestFrom(this.store.pipe(select(selectLikedPostIds))),
          // Process the API response and liked post IDs
          mergeMap(([apiResponse, likedPostIds]) => {
            const results = apiResponse.results as Post[];
            const nextResultExists = apiResponse.next; // Boolean that determines if there is more paginated data

            /*
            - The filter accesses the returned API feed results and looks for posts that have already been liked by 
            the user AND are not present in the centrally shared state 'likedPostIds' (to prevent duplication)
            - The map generates a likePostSuccess action to add each post that is already liked and not in 
            'likedPostIds'.
            */
            const likedPostsToLike = results
              .filter(
                (post) => post.liked_by_user && !likedPostIds.includes(post.id)
              )
              .map((post) => PostActions.likePostSuccess({ postId: post.id }));

            // Effects expect returned actions. The 'loadUserFeedSuccess' action updates the userFeedState with fetched
            // API returned data and 'likedPostsToLike' updates the central state with the unique already liked posts
            return [
              UserFeedActions.loadUserFeedSuccess({
                postData: results,
                hasMoreData: nextResultExists,
              }),
              ...likedPostsToLike,
            ];
          }),
          catchError((error) => {
            console.error(error);
            // Return an observable to continue error propagation
            return of(UserFeedActions.loadUserFeedFailure({ error }));
          })
        )
      )
    )
  );
}
