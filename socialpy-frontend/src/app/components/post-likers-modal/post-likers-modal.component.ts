import { Component, Input, OnInit } from '@angular/core';
import { Router } from '@angular/router';
import {
  InfiniteScrollCustomEvent,
  ModalController,
  ToastController,
} from '@ionic/angular';

import { PostLikersResponse } from 'src/app/interface-types/post-likers.model';

import { PostService } from 'src/app/api-services/post/post.service';
import { FollowService } from 'src/app/api-services/follow/follow.service';

import { faUser, faXmark } from '@fortawesome/free-solid-svg-icons';

@Component({
  selector: 'app-post-likers-modal',
  templateUrl: './post-likers-modal.component.html',
  styleUrls: ['./post-likers-modal.component.css'],
})
export class PostLikersModalComponent implements OnInit {
  @Input() postId!: number;
  constructor(
    private router: Router,
    private postService: PostService,
    private followService: FollowService,
    private modalCtrl: ModalController,
    private toastCtrl: ToastController
  ) {}

  // Contains a list of users who liked a post
  likers: any[] = [];
  currentUserLikersPage = 1; // keep track of the current page of user likers (for pagination)
  hasMoreUserLikersData: boolean = false; // Keeps track if there is more paginated data

  // Font Awesome icons
  faXmark = faXmark;
  faUser = faUser;

  ngOnInit() {
    // Fetch the list of likers when the modal component is initialized
    this.fetchLikers();
  }

  // Call the service api function to retrieve the list of users who liked a post
  async fetchLikers() {
    this.postService
      .postLikersList(this.postId, this.currentUserLikersPage)
      .subscribe({
        next: (data: PostLikersResponse) => {
          this.hasMoreUserLikersData = !!data.next; // Check if there is more paginated data
          this.likers = [...this.likers, ...data.results]; // Append new results to existing likers
        },
        error: (error) => {
          // Handle any errors here
          console.error('Error fetching likers:', error);
        },
      });
  }

  loadMoreLikers(event: Event) {
    // Increment the current page of paginated user likers data
    this.currentUserLikersPage++;

    // Call the service api with the updated page parameter
    this.fetchLikers();

    setTimeout(() => {
      // Complete the infinite scroll event to indicate that loading is done
      (event as InfiniteScrollCustomEvent).target.complete();
      // Scroll back to the previous position
    }, 500);
  }

  // Function to follow a user with a specified id
  followUser(userId: number) {
    // Call the service API function to follow the user
    this.followService.followUser(userId).subscribe({
      next: (response) => {
        if (response && response.follow_status) {
          // Find the index of the user in the likers array
          const userIndex = this.likers.findIndex(
            (liker) => liker.id === userId
          );
          if (userIndex !== -1) {
            // Update the requesting_user_follow_status based on the API response to update the UI
            this.likers[userIndex].requesting_user_follow_status =
              response.follow_status;
          } else {
            console.error(
              'An error occurred while processing your request. Please try again later.'
            );
            // Display a toast message to alert the user an error occured
            this.followUserErrorToast();
          }
        }
      },
      error: (error) => {
        console.error('Error following user:', error);
        // Display a toast message to alert the user an error occured
        this.followUserErrorToast();
      },
    });
  }

  // Display an error ionic toast at the top of the page to alert the user if an error occured
  async followUserErrorToast() {
    const toast = await this.toastCtrl.create({
      message: 'Error following user',
      duration: 1500,
      position: 'top',
    });

    await toast.present();
  }

  // Function to close the modal display
  closeModal() {
    this.modalCtrl.dismiss();
  }

  // Redirect the user to the profile page associated with the user they are attempting to view
  goToUserProfilePage(userId: string) {
    this.closeModal();
    this.router.navigate(['/profile', userId]);
  }
}
