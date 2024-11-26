from django.urls import path
 
from .views import *

urlpatterns = [
    path('login/',AdminLogin.as_view(), name='admin_login'),
    path('forums/', ForumListCreate.as_view(), name='forum-list-create'),
    path('forums/<int:pk>/update/', ForumUpdateView.as_view(), name='forum-update'),
    path('forums/<int:pk>/delete/', ForumDeleteView.as_view(), name='forum-delete'),
    path('speakers/', SpeakerListCreate.as_view(), name='speaker-list-create'),
    path('speakers/<int:pk>/', SpeakerRetrieve.as_view(), name='speaker-detail'),
    path('speakers/<int:pk>/update/', SpeakerUpdateView.as_view(), name='speaker-update'),
    path('speakers/<int:pk>/delete/', SpeakerDeleteView.as_view(), name='speaker-delete'), 
    path('eventcreate/', EventListCreate.as_view() , name='event_create'),
    path('events/', EventListView.as_view(), name='events-list'),  
    path('allevents/', EventListAllView.as_view(), name='allevents-list'),   
    path('events/<int:event_id>/update/', EventUpdateAPIView.as_view(), name='event-update'),
    path('events/<int:pk>/list/', EventListSingleView.as_view(), name='event-detail'),
    path('eventslist/', EventListView.as_view(), name='event-list'),
    path('events/<slug:slug>/', SingleEventDetailView.as_view(), name='single-events-detail'),
    path('enroll/<slug:slug>/single-events/', SingleDetailView.as_view(), name='single-events-enroll'),
    path('events/<slug:slug>/speakers/', EventSpeakersView.as_view(), name='event-speakers'),
    path('eventslistb/', EventListbannerView.as_view(), name='event-list'),
    path('members/', MemberListCreate.as_view(), name='member-list-create'),
    path('members/<int:pk>/update/', MemberUpdateView.as_view(), name='member-update'),
    path('members/<int:pk>/delete/', MemberDeleteView.as_view(), name='member-delete'),
    path('forummembers/', ForumMemberCreateView.as_view(), name='member-create'),
    path('forummembers/<int:forum_id>/', ForumMemberListView.as_view(), name='forum_members_list'),
    path('forummembers/<int:forum_id>/update/', ForumMemberView.as_view(), name='update_forum_member'),
    path('blogs/', CreateBlog.as_view(), name='blog_admin'),
    path('general-blogs/', CreateGeneralBlog.as_view(), name='blog_admin'),
    path('blogslist/', BlogListView.as_view(), name='blog-list'),
    path('blogsgeneral/', GeneralBlogListblog.as_view(), name='blog-list'),
    path('general-blogslist/', GeneralBlogListView.as_view(), name='blog-list'),
    path('blogslistall/', BlogListViewall.as_view(), name='blog-list'),
    path('general-blogslistall/', GeneralBlogListViewall.as_view(), name='blog-list'),
    path('blogs/<int:pk>/delete/', BlogDeleteView.as_view(), name='blogs-delete'),
    path('general-blogs/<int:pk>/delete/', GeneralBlogDeleteView.as_view(), name='blogs-delete'),
    path('blogs/<int:pk>/update/', BlogUpdateView.as_view(), name='forum-update'),
    path('general-blogs/<int:pk>/update/', GeneralBlogUpdateView.as_view(), name='general-blog-update'),
    path('certificates/',CertificatesCreate.as_view(), name='certificate-list-create'),
    path('certificates/<int:pk>/delete', CertificatesDeleteView.as_view(), name='certificates-delete'),
    path('certificateslist/', CertificatesList.as_view(), name='certificates-list'),
    path('certificates/<int:pk>/', CertificatesDetail.as_view(), name='certificate-detail'),
    path('banner/', BannerListCreate.as_view(), name='banner-list-create'),
    path('banner/<int:pk>/update/', BannerUpdateView.as_view(), name='banner-update'),
    path('banner/<int:pk>/delete/', BannerDeleteView.as_view(), name='banner-delete'),
    path('news/', NewsListCreate.as_view(), name='news-list-create'),
    path('news/<int:pk>/update/', NewsUpdateView.as_view(), name='news-update'),
    path('news/<int:pk>/delete/', NewsDeleteView.as_view(), name='news-delete'),
    path('forums/<int:forum_id>/members/', ForumMemberList.as_view(), name='forum-members'), 
    path('forums_get/',  ForumListView.as_view(), name='forum-get'),
    path('forums_get_member/',  ForumLisMembertView.as_view(), name='forum-get_member'),
    path('members_exclude/<int:forum_id>/', ForumExcludeView.as_view(), name='forum_exclude'),
    path('boards/', BoardListCreate.as_view(), name='boards-list-create'),
    path('boards/<int:pk>/update/', BoardUpdateView.as_view(), name='board-update'),
    path('boards/<int:pk>/delete/', BoardDeleteView.as_view(), name='board-delete'),
    path('boards_get/',  BoardListView.as_view(), name='board-get'),
    path('boards_get_member/',  BoardLisMembertView.as_view(), name='board-get_member'),
    path('members_exclude/<int:board_id>/', BoardExcludeView.as_view(), name='board_exclude'),
    path('boardmembers/', BoardMemberCreateView.as_view(), name='member-create'),
    path('boardmembers/<int:board_id>/', BoardMemberListView.as_view(), name='board_members_list'),
    path('boardmembers/<int:board_id>/update/', BoardMemberView.as_view(), name='board_board_member'),
    path('allboardmembers/', AllBoardMembersView.as_view(), name='all_board_members'),
    path('commboardmembers/', CommitteeMembersView.as_view(), name='all_board_members'),
    path('members/<slug:slug>/detail/', MemberDetailViewBySlug.as_view(), name='member_detail_by_slug'),
    path('forums/<slug:slug>/', EventForumListView.as_view(), name='forum-events'),
    path('blogsforum/<slug:slug>/', BlogForumListView.as_view(), name='blog-list'),
    path('forumsyear/<slug:slug>/', EventForumYearView.as_view(), name='forum-events'),
    path('blogsyear/<slug:slug>/', BlogForumYearView.as_view(), name='blog-list'),
    path('forum/<slug:slug>/events/', EventTodayView.as_view(), name='event-forum-list'),
    path('forumweek/<slug:slug>/events/', EventThisWeekView.as_view(), name='eventweek-forum-list'),
    path('forummonth/<slug:slug>/events/', EventThisMonthView.as_view(), name='eventmonth-forum-list'),
    path('forumyear/<slug:slug>/events/', EventThisYearView.as_view(), name='eventyear-forum-list'),
    path('blogs-detail/<slug:slug>/', BlogDetailView.as_view(), name='blog-detail'),
    path('general-blogs-detail/<slug:slug>/', BlogGeneralDetailView.as_view(), name='blog-detail'),
    path('eventstoday/', EventUserToday.as_view(), name='event-today-list'),
    path('eventsweek/', EventUserThisWeek.as_view(), name='event-week-list'),
    path('eventsmonth/', EventThisMonthUser.as_view(), name='event-month-list'),
    path('eventsyear/', EventThisYearUser.as_view(), name='event-year-list'),
    path('add-gallery/', AddGalleryView.as_view(), name='add-gallery'),
    path('gallery/', GetGalleryView.as_view(), name='get_gallery_images'),
    path('update-gallery/<int:pk>/', UpdateGalleryView.as_view(), name='update_gallery'),
    path('delete-gallery/<int:gallery_id>/', DeleteGalleryView.as_view(), name='delete_gallery'),
    path('events/<int:event_id>/delete/', EventDeleteAPIView.as_view(), name='event-delete'),
    path('upload/', UploadAttachmentView.as_view(), name='upload_attachment'),
    path('single-events-all/', SingleEventListAllView.as_view(), name='single-event-list'),
    path('general-single-events-all/', SingleGeneralEventListAllView.as_view(), name='update-attachment'),   
    path('general_attachments/<slug:slug>/', GeneralAttachmentsBySingleEventView.as_view(), name='general-attachments'),
    path('attachments/<slug:slug>/', AttachmentsBySingleEventView.as_view(), name='event-attachments'),    
    path('attachments-all/', ListAttachmentsView.as_view(), name='list-attachments'),
    path('attachments/<int:pk>/delete/', AttachmentDeleteAPIView.as_view(), name='attachment-delete'),
    path('user-file-interaction/', AssociateFileWithUserView.as_view(), name='user-file-interaction'),
    path('user-attachments/', UserAttachmentsView.as_view(), name='user-attachments'),
    path('general-user-attachments/', GeneralUserAttachmentsView.as_view(), name='user-attachments'),
    path('attachments/<int:pk>/update/', AttachmentUpdateAPIView.as_view(), name='attachment-update'),
    path('check-auth/', CheckAuthView.as_view(), name='check_auth'),
    path('logout/', AdminLogout.as_view(), name='admin-logout'),
    path('general_eventcreate/', GeneralEventListCreate.as_view() , name='event_create'),
    path('general_allevents/', GeneralEventListAllView.as_view(), name='allevents-list'),
    path('general_events/<int:event_id>/delete/', GeneralEventDeleteAPIView.as_view(), name='event-delete'),
    path('general_events/<int:event_id>/update/', GeneralEventUpdateAPIView.as_view(), name='general-event-update'),
    path('general_events/', GeneralEventListView.as_view(), name='general-events-list'),  
    path('general_singleevents_all/', GeneralSingleEventListAllView.as_view(), name='general-single-event-list'),
    path('generalevents/<slug:slug>/', GeneralSingleEventDetailView.as_view(), name='single-events-detail'),
    path('general_events/<slug:slug>/speakers/', GeneralEventSpeakersView.as_view(), name='event-speakers'),
    path('general_events/<slug:slug>/', GeneralSingleEventDetailView.as_view(), name='single-events-detail'),
    path('general_enroll/<slug:slug>/single-events/', GeneralSingleDetailView.as_view(), name='single-events-enroll'),
    path('general_certificateslist/', GeneralCertificatesList.as_view(), name='certificates-list'),
    path('general_certificates/',GeneralCertificatesCreate.as_view(), name='certificate-list-create'),
    path('general_certificates/<int:pk>/', GeneralCertificatesDetail.as_view(), name='certificate-detail'),
    path('general_certificates/<int:pk>/delete', GeneralCertificatesDeleteView.as_view(), name='certificates-delete'),
    path('general_eventstoday/', GeneralEventUserToday.as_view(), name='event-today-list'),
    path('general_eventsweek/', GeneralEventUserThisWeek.as_view(), name='event-week-list'),
    path('general_eventsmonth/', GeneralEventThisMonthUser.as_view(), name='event-month-list'),
    path('general_eventsyear/', GeneralEventThisYearUser.as_view(), name='event-year-list'),
    path('general_eventslistb/', GeneralEventListbannerView.as_view(), name='event-list'),
    path('general_upload/', GeneralUploadAttachmentView.as_view(), name='upload_attachment'),
    path('general_attachments-all/', GeneralListAttachmentsView.as_view(), name='list-attachments'),
    path('general_attachments/<int:pk>/delete/', GeneralAttachmentDeleteAPIView.as_view(), name='attachment-delete'),
    path('general_attachments/<int:pk>/update/', GeneralAttachmentUpdateAPIView.as_view(), name='attachment-update'),
    path('newsletters/', NewsletterListCreateView.as_view(), name='newsletter-list-create'),
    path('newsletterslist/', NewsletterListView.as_view(), name='newsletter-list'),
    path('newsletters/<int:pk>/delete/', NewsletterDeleteView.as_view(), name='newsletter-delete'),
    path('newsletters/<int:pk>/update/', NewsletterUpdateView.as_view(), name='update_newsletter'),
    # path('general_attachments/', GeneralAttachmentsBySingleEventView.as_view(), name='retrieve-attachment'),
    path('general_user-file-interaction/', GeneralAssociateFileWithUserView.as_view(), name='user-file-interaction'),
    path('podcast/', CreatePodcast.as_view(), name='blog_admin'),
    path('podcast_listall/', PodcastListViewall.as_view(), name='blog-list'),
    path('podcast/<int:pk>/delete/', PodcastDeleteView.as_view(), name='podcast-delete'),
    path('podcast/<int:pk>/update/', PodcastUpdateView.as_view(), name='podcast-update'),
    path('podcasts_list/', PodcastListView.as_view(), name='podcast-list'),
    path('podcast/<str:name>/', PodcastDetailView.as_view(), name='podcast-detail'),
    path('total-events/', TotalEventCountView.as_view(), name='total-events'),
    path('member-count/', MemberCountAPIView.as_view(), name='member-count-api'),
    path('speaker-count/', SpeakerCountAPIView.as_view(), name='speaker-count-api'),
    path('newsletter-count/',  NewsletterCountAPIView.as_view(), name='speaker-count-api'),
    path('podcast-count/',  PodcastCountAPIView.as_view(), name='speaker-count-api'),
    path('events/<int:event_id>/attachments/', SingleEventAttachmentsView.as_view(), name='event-attachments'),
    path('general-events/<int:event_id>/attachments/', GeneralSingleEventAttachmentsView.as_view(), name='general-event-attachments'),
   
]     
 