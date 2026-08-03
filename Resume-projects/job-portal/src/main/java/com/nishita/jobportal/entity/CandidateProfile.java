package com.nishita.jobportal.entity;

import jakarta.persistence.*;

@Entity @Table(name="candidate_profiles")
public class CandidateProfile {
    @Id @GeneratedValue(strategy=GenerationType.IDENTITY) private Long id;
    @OneToOne(optional=false) @JoinColumn(name="user_id", unique=true) private UserAccount user;
    private String headline; private String location;
    @Column(length=2000) private String bio;
    @Column(length=1000) private String skills;
    private String resumePath;
    public Long getId(){return id;} public UserAccount getUser(){return user;} public void setUser(UserAccount user){this.user=user;}
    public String getHeadline(){return headline;} public void setHeadline(String v){headline=v;}
    public String getLocation(){return location;} public void setLocation(String v){location=v;}
    public String getBio(){return bio;} public void setBio(String v){bio=v;}
    public String getSkills(){return skills;} public void setSkills(String v){skills=v;}
    public String getResumePath(){return resumePath;} public void setResumePath(String v){resumePath=v;}
}
