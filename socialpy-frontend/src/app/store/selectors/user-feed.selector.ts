import { createSelector, createFeatureSelector } from '@ngrx/store';
import { UserFeedState } from '../user-feed/user-feed.reducer';

/* 
Create a feature selector to select the userFeed feature state. Feature selectors access the state of a specific 
feature module within the store. In this case, it selects the 'userFeed' feature state from the store.
*/
const selectUserFeedFeature = createFeatureSelector<UserFeedState>('userFeed');

// Selectors are used to make a central mechanism to allow different components and effect middlewares to 
// efficiently access and change data from the store's state.

// Create a selector function to select the entire UserFeedState including properties like 'loading', 'error', and 'postData'.
export const selectUserFeedState = createSelector(
  selectUserFeedFeature,
  (state: UserFeedState) => state
);

/* 
Selector function to select the 'postData' property from the 'userFeed' feature state. This allows components 
and effect middlewares to efficiently access the user feed data.
*/
export const selectUserFeedData = createSelector(
  selectUserFeedState, // Use the selectUserFeedState selector
  (state: UserFeedState) => state.postData
);

/* 
Selector function to select the 'loading' property from the 'userFeed' feature state. This enables components and 
effect middlewares to efficiently access the loading state, which indicates if data is being fetched.
*/
export const selectUserFeedLoading = createSelector(
  selectUserFeedState, // Use the selectUserFeedState selector
  (state: UserFeedState) => state.loading
);

/* 
Selector function to select the 'error' property from the 'userFeed' feature state. This allows components and 
effect middlewares to efficiently access error information if any errors occur during data retrieval.
*/
export const selectUserFeedError = createSelector(
  selectUserFeedState, // Use the selectUserFeedState selector
  (state: UserFeedState) => state.error
);
