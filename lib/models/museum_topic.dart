class MuseumTopic {
  final String id;
  final String groupId;
  final String title;
  final String summary;
  final String materialsNotes;
  final String sourceReference;
  final String reviewStatus;

  const MuseumTopic({
    required this.id,
    required this.groupId,
    required this.title,
    required this.summary,
    required this.materialsNotes,
    required this.sourceReference,
    required this.reviewStatus,
  });

  String get name => title;
  String get description => summary;

  factory MuseumTopic.fromJson(Map<String, dynamic> json) => MuseumTopic(
        id: json['id'] as String,
        groupId: json['group_id'] as String,
        title: json['title'] as String,
        summary: json['summary'] as String,
        materialsNotes: json['materials_notes'] as String,
        sourceReference: json['source_reference'] as String,
        reviewStatus: json['review_status'] as String,
      );
}
