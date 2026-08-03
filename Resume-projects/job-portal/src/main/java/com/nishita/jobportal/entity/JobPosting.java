package com.nishita.jobportal.entity;

import jakarta.persistence.*;
import java.time.Instant;

@Entity @Table(name="job_postings")
public class JobPosting {
    @Id @GeneratedValue(strategy=GenerationType.IDENTITY) private Long id;
    @ManyToOne(optional=false) private Company company;
    @Column(nullable=false) private String title;
    @Column(nullable=false, length=4000) private String description;
    @Column(nullable=false) private String location;
    @Column(nullable=false) private String employmentType;
    @Column(nullable=false, length=1000) private String skills;
    private Integer salaryMin; private Integer salaryMax;
    @Enumerated(EnumType.STRING) @Column(nullable=false) private JobStatus status=JobStatus.OPEN;
    @Column(nullable=false) private Instant createdAt=Instant.now();
    public Long getId(){return id;} public Company getCompany(){return company;} public void setCompany(Company v){company=v;}
    public String getTitle(){return title;} public void setTitle(String v){title=v;} public String getDescription(){return description;} public void setDescription(String v){description=v;}
    public String getLocation(){return location;} public void setLocation(String v){location=v;} public String getEmploymentType(){return employmentType;} public void setEmploymentType(String v){employmentType=v;}
    public String getSkills(){return skills;} public void setSkills(String v){skills=v;} public Integer getSalaryMin(){return salaryMin;} public void setSalaryMin(Integer v){salaryMin=v;}
    public Integer getSalaryMax(){return salaryMax;} public void setSalaryMax(Integer v){salaryMax=v;} public JobStatus getStatus(){return status;} public void setStatus(JobStatus v){status=v;}
    public Instant getCreatedAt(){return createdAt;}
}
