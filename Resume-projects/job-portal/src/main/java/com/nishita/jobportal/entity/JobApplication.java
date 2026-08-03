package com.nishita.jobportal.entity;

import jakarta.persistence.*;
import java.time.Instant;

@Entity @Table(name="applications", uniqueConstraints=@UniqueConstraint(columnNames={"job_id","candidate_id"}))
public class JobApplication {
    @Id @GeneratedValue(strategy=GenerationType.IDENTITY) private Long id;
    @ManyToOne(optional=false) @JoinColumn(name="job_id") private JobPosting job;
    @ManyToOne(optional=false) @JoinColumn(name="candidate_id") private UserAccount candidate;
    @Column(length=2000) private String coverNote;
    @Enumerated(EnumType.STRING) @Column(nullable=false) private ApplicationStatus status=ApplicationStatus.APPLIED;
    @Column(nullable=false) private Instant appliedAt=Instant.now();
    public Long getId(){return id;} public JobPosting getJob(){return job;} public void setJob(JobPosting v){job=v;}
    public UserAccount getCandidate(){return candidate;} public void setCandidate(UserAccount v){candidate=v;}
    public String getCoverNote(){return coverNote;} public void setCoverNote(String v){coverNote=v;}
    public ApplicationStatus getStatus(){return status;} public void setStatus(ApplicationStatus v){status=v;} public Instant getAppliedAt(){return appliedAt;}
}
